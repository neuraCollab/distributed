#ifndef PAGE_FETCHER_H
#define PAGE_FETCHER_H

#include <string>

struct MemoryStruct {
    char *memory;
    size_t size;
};

// Функция для загрузки веб-страницы по URL
void fetchPage(const std::string &url, MemoryStruct &chunk);

#endif // PAGE_FETCHER_H
