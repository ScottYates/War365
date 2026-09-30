// War365 dev server. Serves the static site from this directory.
//
// Usage:
//	go run .                  # listen on http://localhost:8000
//	go run . -addr=:8765      # custom port
//
// All four static assets are baked into the binary via //go:embed, so the
// server is a single self-contained executable once built. Add new site
// assets to the embed list below when you add them.
package main

import (
	"embed"
	"flag"
	"log"
	"net/http"
)

//go:embed index.html styles.css commits.js app.js
var assets embed.FS

func main() {
	addr := flag.String("addr", ":8000", "address to listen on")
	flag.Parse()
	log.Printf("war365 dev server: http://localhost%s", *addr)
	log.Fatal(http.ListenAndServe(*addr, http.FileServer(http.FS(assets))))
}
