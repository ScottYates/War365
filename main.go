// War365 dev server. Serves the static site from this directory on disk.
//
// Usage:
//	go run .                  # listen on http://localhost:8000
//	go run . -addr=:8765      # custom port
//
// Files are read from disk on each request, so edits to HTML/CSS/JS show up
// on a browser refresh with no rebuild. Must be run from the project root so
// relative paths resolve.
//
// os.DirFS is used (rather than http.Dir) so the server is restricted to
// the current directory and its subdirectories — requests with parent-dir
// segments ("..") are refused by the stdlib, preventing path traversal.
package main

import (
	"flag"
	"log"
	"net/http"
	"os"
)

func main() {
	addr := flag.String("addr", ":8000", "address to listen on")
	flag.Parse()
	log.Printf("war365 dev server: http://localhost%s (serving current directory)", *addr)
	log.Fatal(http.ListenAndServe(*addr, http.FileServer(http.FS(os.DirFS(".")))))
}

