.PHONY: pdf clean

pdf:
	latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error -pdflatex='pdflatex -no-shell-escape %O %S' -outdir=build main.tex
	cp build/main.pdf main.pdf

clean:
	latexmk -C -outdir=build main.tex
