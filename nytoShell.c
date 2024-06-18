#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_log.h"

#define MAX_COMMAND_LENGTH 1024
#define MAX_ARGUMENTS 20
static const char *TAG = "shell";

// Function to read user input
void read_command(char cmd[], char *par[]) {
    char line[MAX_COMMAND_LENGTH];
    fgets(line, sizeof(line), stdin);
    // Tokenize the input
    char *token = strtok(line, " \n");
    int i = 0;
    while (token != NULL) {
        par[i++] = strdup(token);
        token = strtok(NULL, " \n");
    }
    par[i] = NULL;
    strcpy(cmd, par[0]);
}

// Function to execute external commands
void execute_command(char *cmd, char *par[]) {
    // ESP32 doesn't support fork(), so we can't execute external commands
    ESP_LOGI(TAG, "External command execution is not supported on ESP32.");
}

// Function to handle built-in commands
int handle_builtin_commands(char *cmd, char *par[]) {
    if (strcmp(cmd, "exit") == 0) {
        // Exit the shell
        vTaskDelete(NULL); // Terminate the current task
        return 1;
    }
    return 0; // Not a built-in command
}

// Function to display prompt
void display_prompt() {
    ESP_LOGI(TAG, "$ ");
}

void shell_task(void *pvParameters) {
    char cmd[MAX_COMMAND_LENGTH], *parameters[MAX_ARGUMENTS];
    while (1) {
        display_prompt();
        read_command(cmd, parameters);
        // Check if command is a built-in command
        if (handle_builtin_commands(cmd, parameters)) {
            continue; // Continue to next iteration of the loop
        }
        // Execute external command
        execute_command(cmd, parameters);
    }
}

void app_main() {
    xTaskCreate(shell_task, "shell_task", 4096, NULL, 5, NULL);
}
