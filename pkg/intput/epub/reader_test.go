package epub

import (
	"log"
	"testing"
)

const (
	fileName = "/Users/macbook/Documents/project/library/css/CSS揭秘.epub"
)

func TestReader_ParseReferences(t *testing.T) {
	reader, err := NewReader(fileName)
	if err != nil {
		log.Fatal(err)
	}
	references, err := reader.ParseReferences()
	log.Fatal(references, err)
}
