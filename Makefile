.PHONY : all
all : main.pdf

./%.pdf : ./%.tex ./%.toc ./%.glo $(shell find ./sections -iname "*.tex") $(shell find ./img -iname "*.png" -o -iname "*.jpg" -o -iname "*.pdf")
	pdflatex $<

./%.toc : ./%.tex
	pdflatex $<

./main.glo : ./glossary.tex
	pdflatex main.tex

.PHONY : doc docx word
doc docx word : ./main.docx

./%.docx : ./%.tex ./%.toc ./%.glo $(shell find ./sections -iname "*.tex") $(shell find ./img -iname "*.png" -o -iname "*.jpg" -o -iname "*.pdf")
	pandoc -so $@ $<

.PHONY : clean
clean :
	rm -rf *.{pdf,docx,aux,lof,glo,log,ist,toc,out}
