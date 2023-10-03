#include "commands.h"

int command_init(struct command *cmd)
{
    cmd->filepath = NULL;
    cmd->name = NULL;
    cmd->execute = NULL;
    return 0;
}

int command_set_name(struct command *cmd, const char *name)
{
    size_t size = sizeof(char) * strlen(name);
    cmd->name = (char*)malloc(size);
    if(cmd->name == NULL){
        printf("failed to allocate space for command name\n");
        return 1;
    }
    memcpy(cmd->name, name, size);
    return 0;
}

int command_set_filepath(struct command *cmd, const char *filepath)
{
    size_t size = sizeof(char) * strlen(filepath);
    cmd->filepath = (char*)malloc(size);
    if(cmd->filepath == NULL){
        printf("failed to allocate space for command filepath\n");
        return 1;
    }
    memcpy(cmd->filepath, filepath, size);
    return 0;
}

int command_free(struct command *cmd)
{
    if(cmd->name != NULL){
        free(cmd->name);
        cmd->name = NULL;
    }
    if(cmd->filepath != NULL){
        free(cmd->filepath);
        cmd->filepath = NULL;
    }
    if(cmd->execute != NULL){
        free(cmd->execute);
        cmd->execute = NULL;
    }
    return 0;
}

int command_cache_init(struct command_cache *cache)
{
    cache->commands_count = 0;
    cache->commands = (struct command*)malloc(sizeof(struct command*));
    return 0;
}

int command_cache_add(struct command_cache *cache, struct command *cmd)
{
    size_t size = sizeof(struct command*) * (cache->commands_count + 1);
    struct command* new_commands = (struct command*)realloc(cache->commands, size);
    if(new_commands == NULL){
        printf("failed to allocate space for commands\n");
        return 1;
    }
    new_commands[cache->commands_count+1] = *cmd;
    cache->commands_count++;
    return 0;
}

int command_cache_get_by_name(struct command_cache *cache, const char *text, struct command* out)
{
    for(size_t i = 0; i < cache->commands_count; i++){
        struct command cmd = cache->commands[i];
        if(cmd.name == NULL) continue;
        if(strcmp(cmd.name, text)){
            out = &cmd;
            break;
        }
    }
    return 0;
}

int command_cache_free(struct command_cache *cache)
{
    for(size_t i = 0; i < cache->commands_count; i++){
        struct command cmd = cache->commands[i];
        int retvalue = command_free(&cmd);
        if(retvalue != 0){
            printf("failed to free command\n");
            return 1;
        }
    }
    return 0;
}
