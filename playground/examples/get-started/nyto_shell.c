#include <stdio.h>

void app_main(void)
{
    char cmd[MAX_COMMAND_LENGTH], *parameters[MAX_ARGUMENTS];
    while (1) {
        display_prompt();
        read_command(cmd, parameters);
        // Check if command is empty
        if (cmd[0] == '\0') {
            continue; // Skip this iteration if no command was entered
        }
        // Check if command is a built-in command
        if (handle_builtin_commands(cmd, parameters)) {
            // Free dynamically allocated memory
            for (int i = 0; parameters[i] != NULL; i++) {
                free(parameters[i]);
            }
            continue; // Continue to next iteration of the loop
        }
        // Execute external command
        execute_command(cmd, parameters);
        // Free dynamically allocated memory
        for (int i = 0; parameters[i] != NULL; i++) {
            free(parameters[i]);
        }
    }
}
