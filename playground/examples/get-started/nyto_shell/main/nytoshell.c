#include <stdio.h>
#include <stdbool.h>
#include <string.h>

#define MAX_COMMAND_LENGTH 100
#define MAX_ARGUMENTS 10

void display_prompt(void) {
  printf("nyto_shell> ");
}

void read_command(char *cmd, char **parameters) {
  // Read the entire line from stdin
  fgets(cmd, MAX_COMMAND_LENGTH, stdin);

  // Remove trailing newline character
  if (strchr(cmd, '\n') != NULL) {
    cmd[strcspn(cmd, "\n")] = '\0';
  }

  // Parse the command and arguments
  int num_args = 0;
  char *token = strtok(cmd, " ");
  if (token != NULL) {
    parameters[num_args++] = token;
    while ((token = strtok(NULL, " ")) != NULL) {
      if (num_args >= MAX_ARGUMENTS) {
        printf("Error: Too many arguments\n");
        break;
      }
      parameters[num_args++] = token;
    }
  }
  // Set remaining parameters to NULL
  for (int i = num_args; i < MAX_ARGUMENTS; i++) {
    parameters[i] = NULL;
  }
}

bool handle_builtin_commands(char *cmd, char **parameters) {
  if (strcmp(cmd, "exit") == 0) {
    printf("Exiting nyto_shell\n");
    return true;
  } else if (strcmp(cmd, "help") == 0) {
    printf("Available commands:\n");
    printf("  exit - Exit the shell\n");
    printf("  help - Show this help message\n");
    // Add help messages for other built-in commands here
    return true;
  }
  // Add more built-in commands here
  return false;
}

void execute_command(char *cmd, char **parameters) {
  // Implement logic to execute external commands using system calls or other methods
  printf("External command '%s' not implemented yet\n", cmd);
}

