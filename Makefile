main: Main.cpp *.h
	g++ -O2 -g -std=c++11 -lpthread -pthread Main.cpp -o main
