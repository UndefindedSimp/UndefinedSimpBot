#pragma once
#ifndef COMMANDS_H
#define COMMANDS_H

#include "stdio.h"
#include "stdlib.h"
#include "string.h"

#include "concord/discord.h"

struct command_context {
    struct discord_client* client;
};

struct command {
    char* name;
    void (*execute)();
    char* filepath;
};

struct command_cache {
    size_t commands_count;
    struct command* commands;
};

int command_init(struct command* cmd);
int command_set_name(struct command* cmd, const char* name);
int command_set_filepath(struct command* cmd, const char* filepath);
int command_free(struct command* cmd);

int command_cache_init(struct command_cache* cache);
int command_cache_add(struct command_cache* cache, struct command* cmd);
int command_cache_get_by_name(struct command_cache *cache, const char *text, struct command* out);
int command_cache_free(struct command_cache* cache);

#endif