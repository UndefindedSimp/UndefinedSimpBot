CXX= gcc
CFLAGS= -Wall -Werror 
TARGET= main

LIBFLAGS= -pthread -ldiscord -lcurl

all: link build

link:

build:
	$(CXX) $(TARGET).c -o $(TARGET) $(CFLAGS)