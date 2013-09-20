package main

import (
	"log"
	"net/http"
)

func main() {
	// Simple static webserver:
	log.Fatal(http.ListenAndServe("0.0.0.0:8080", http.FileServer(http.Dir("finished_jobs"))))
}
