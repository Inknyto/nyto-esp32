idf_component_register(
  SRCS
    "main.c"
    "nytoshell.c"
  INCLUDE_DIRS
    "../esp32/gdb"
    "../esp32/config"
    "../esp32/xtensa/config"
  REQUIRES
    freertos
    soc
)

