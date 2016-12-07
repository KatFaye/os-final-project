CXX=		g++
CXXFLAGS=	-g -Wall -std=gnu++11

test: crawler.py
	./crawler.py

test-all: test.sh crawler.py measure
	./test.sh

measure: measure.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^
