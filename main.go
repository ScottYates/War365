// War365 dev server. Serves the static site from this directory on disk.
//
// Usage:
//	go run .                       # listen on http://localhost:8000
//	go run . -addr=:8765           # custom port
//	go run . -quiet                # no per-request access log
//	go run . -log-format=json      # structured logs for log shipping
//	go run . -log-level=debug      # debug, info, warn, error
//
// Files are read from disk on each request, so edits to HTML/CSS/JS show up
// on a browser refresh with no rebuild. Must be run from the project root so
// relative paths resolve.
//
// os.DirFS is used (rather than http.Dir) so the server is restricted to
// the current directory and its subdirectories — requests with parent-dir
// segments ("..") are refused by the stdlib, preventing path traversal.
//
// Logs go to stdout. Under systemd both stdout and stderr reach the journal,
// so `journalctl -u war365 -f` picks up everything.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"log/slog"
	"net"
	"net/http"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"
)

// shutdownTimeout matches TimeoutStopSec in deploy/war365.service.
const shutdownTimeout = 10 * time.Second

func main() {
	addr := flag.String("addr", ":8000", "address to listen on")
	logFormat := flag.String("log-format", "text", "log output format: text or json")
	logLevel := flag.String("log-level", "info", "log level: debug, info, warn, error")
	logFile := flag.String("log-file", "", "also append logs to this file (default: stdout only)")
	quiet := flag.Bool("quiet", false, "suppress per-request access logs")
	flag.Parse()

	logger, closeLog, err := newLogger(*logFormat, *logLevel, *logFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}
	defer closeLog()
	slog.SetDefault(logger)

	var handler http.Handler = http.FileServer(http.FS(os.DirFS(".")))
	if !*quiet {
		handler = requestLogger(logger, handler)
	}

	srv := &http.Server{
		Addr:    *addr,
		Handler: handler,
		// Route net/http's own errors (broken pipes, TLS handshakes) into
		// the same logger instead of the default one on stderr.
		ErrorLog: slog.NewLogLogger(logger.Handler(), slog.LevelWarn),
	}

	// systemd sends SIGTERM on stop; SIGINT covers Ctrl-C during `go run`.
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	serveErr := make(chan error, 1)
	go func() {
		logger.Info("war365 starting", "addr", *addr, "dir", ".",
			"access_log", !*quiet, "log_file", *logFile)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			serveErr <- err
			return
		}
		serveErr <- nil
	}()

	select {
	case err := <-serveErr:
		if err != nil {
			logger.Error("server failed", "err", err)
			os.Exit(1)
		}
	case <-ctx.Done():
		logger.Info("shutdown requested, draining connections")
	}

	sctx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
	defer cancel()
	if err := srv.Shutdown(sctx); err != nil {
		logger.Error("graceful shutdown failed", "err", err)
		os.Exit(1)
	}
	logger.Info("war365 stopped")
}

func newLogger(format, level, path string) (*slog.Logger, func(), error) {
	var lvl slog.Level
	if err := lvl.UnmarshalText([]byte(level)); err != nil {
		lvl = slog.LevelInfo
	}
	opts := &slog.HandlerOptions{Level: lvl}

	// With no -log-file, log to stdout only (journald under systemd, terminal
	// otherwise).
	var sink io.Writer = os.Stdout
	closer := func() {}

	if path != "" {
		if dir := filepath.Dir(path); dir != "" && dir != "." {
			if err := os.MkdirAll(dir, 0o755); err != nil {
				return nil, nil, fmt.Errorf("create log dir %s: %w", dir, err)
			}
		}
		// O_APPEND, never O_TRUNC: a restart must add to the existing log, and
		// O_APPEND makes each write atomic so concurrent lines cannot interleave.
		f, err := os.OpenFile(path, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
		if err != nil {
			return nil, nil, fmt.Errorf("open log file %s: %w", path, err)
		}
		// Keep stdout too, so `journalctl -u war365` still works when a file
		// sink is configured.
		sink = io.MultiWriter(f, os.Stdout)
		closer = func() { _ = f.Close() }
	}

	var h slog.Handler
	if strings.EqualFold(format, "json") {
		h = slog.NewJSONHandler(sink, opts)
	} else {
		h = slog.NewTextHandler(sink, opts)
	}
	return slog.New(h), closer, nil
}

// statusRecorder captures the status code and byte count that the underlying
// ResponseWriter sees, so they can be logged after the handler returns.
type statusRecorder struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (r *statusRecorder) WriteHeader(code int) {
	if r.status == 0 {
		r.status = code
	}
	r.ResponseWriter.WriteHeader(code)
}

func (r *statusRecorder) Write(b []byte) (int, error) {
	if r.status == 0 {
		r.status = http.StatusOK
	}
	n, err := r.ResponseWriter.Write(b)
	r.bytes += n
	return n, err
}

// requestLogger logs one line per request. The log runs in a defer so a
// panicking handler still produces an access line.
func requestLogger(logger *slog.Logger, next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w}
		defer func() {
			if rec.status == 0 {
				rec.status = http.StatusOK
			}
			// 5xx is a server-side fault, so it earns a louder level.
			level := slog.LevelInfo
			if rec.status >= 500 {
				level = slog.LevelError
			}
			logger.LogAttrs(r.Context(), level, "request",
				slog.String("method", r.Method),
				slog.String("path", r.URL.RequestURI()),
				slog.Int("status", rec.status),
				slog.Int("bytes", rec.bytes),
				// Integer ms rather than slog.Duration, which serialises as
				// raw nanoseconds and is unreadable in a log line.
				slog.Int("took_ms", int(time.Since(start).Milliseconds())),
				slog.String("remote", clientIP(r)),
			)
		}()
		next.ServeHTTP(rec, r)
	})
}

// clientIP prefers the first X-Forwarded-For entry. That is only trustworthy
// when the reverse proxy overwrites the header rather than appending to it;
// otherwise the value is client-controlled and this is log cosmetics only.
func clientIP(r *http.Request) string {
	if xff := r.Header.Get("X-Forwarded-For"); xff != "" {
		if i := strings.IndexByte(xff, ','); i >= 0 {
			return strings.TrimSpace(xff[:i])
		}
		return strings.TrimSpace(xff)
	}
	if host, _, err := net.SplitHostPort(r.RemoteAddr); err == nil {
		return host
	}
	return r.RemoteAddr
}
