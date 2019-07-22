package zip

import (
	"archive/zip"
	"fmt"
	"log"
	"testing"
)

const (
	name = "/Users/macbook/Documents/project/library/css/CSS权威指南第三版.epub"
)

type A struct {
	a string
}

type B struct {
	A
	b string
}

func TestNewReader(t *testing.T) {
	reader, err := NewReader(name)
	if err != nil {
		log.Fatal(err)
	}
	reader.Range(func(file *zip.File) bool {
		fmt.Printf("%s - %v\n", file.Name, file.Mode())
		return true
	})
}
