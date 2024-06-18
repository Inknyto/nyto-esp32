/*
 * SPDX-FileCopyrightText: 2021-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Unlicense OR CC0-1.0
 */

#include <stdint.h>
#include <math.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/i2s_pdm.h"
#include "driver/gpio.h"
#include "esp_check.h"
#include "sdkconfig.h"
#include "i2s_pdm_example.h"

#define EXAMPLE_PDM_TX_CLK_IO           GPIO_NUM_4      // I2S PDM TX clock io number
#define EXAMPLE_PDM_TX_DOUT_IO          GPIO_NUM_5      // I2S PDM TX data out io number

#define EXAMPLE_PDM_TX_FREQ_HZ          44100           // I2S PDM TX frequency
#define EXAMPLE_WAVE_AMPLITUDE          (1000.0)        // 1~32767
#define CONST_PI                        (3.1416f)
#define EXAMPLE_SINE_WAVE_LEN(tone)     (uint32_t)((EXAMPLE_PDM_TX_FREQ_HZ / (float)tone) + 0.5) // The sample point number per sine wave to generate the tone
#define EXAMPLE_TONE_LAST_TIME_MS       500
#define EXAMPLE_BYTE_NUM_EVERY_TONE     (EXAMPLE_TONE_LAST_TIME_MS * EXAMPLE_PDM_TX_FREQ_HZ / 1000)

/* The frequency of tones: do, re, mi, fa, so, la, si, in Hz. */
static const uint32_t tone[3][7] = {
    {262, 294, 330, 349, 392, 440, 494},        // bass
    {523, 587, 659, 698, 784, 880, 988},        // alto
    {1046, 1175, 1318, 1397, 1568, 1760, 1976}, // treble
};
/* Numbered musical notation of 'twinkle twinkle little star' */
static const uint8_t song[28] = {1, 1, 5, 5, 6, 6, 5,
                                 4, 4, 3, 3, 2, 2, 1,
                                 5, 5, 4, 4, 3, 3, 2,
                                 5, 5, 4, 4, 3, 3, 2
                                };
/* Rhythm of 'twinkle twinkle little star', it's repeated in four sections */
static const uint8_t rhythm[7] = {1, 1, 1, 1, 1, 1, 2};

static const char *tone_name[3] = {"bass", "alto", "treble"};

static i2s_chan_handle_t i2s_example_init_pdm_tx(void)
{
    i2s_chan_handle_t tx_chan;        // I2S tx channel handler
    /* Setp 1: Determine the I2S channel configuration and allocate TX channel only
     * The default configuration can be generated by the helper macro,
     * it only requires the I2S controller id and I2S role,
     * but note that PDM channel can only be registered on I2S_NUM_0 */
    i2s_chan_config_t tx_chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_AUTO, I2S_ROLE_MASTER);
    tx_chan_cfg.auto_clear = true;
    ESP_ERROR_CHECK(i2s_new_channel(&tx_chan_cfg, &tx_chan, NULL));

    /* Step 2: Setting the configurations of PDM TX mode and initialize the TX channel
     * The slot configuration and clock configuration can be generated by the macros
     * These two helper macros is defined in 'i2s_pdm.h' which can only be used in PDM TX mode.
     * They can help to specify the slot and clock configurations for initialization or re-configuring */
    i2s_pdm_tx_config_t pdm_tx_cfg = {
#if CONFIG_EXAMPLE_PDM_TX_DAC
        .clk_cfg = I2S_PDM_TX_CLK_DAC_DEFAULT_CONFIG(EXAMPLE_PDM_TX_FREQ_HZ),
        /* The data bit-width of PDM mode is fixed to 16 */
        .slot_cfg = I2S_PDM_TX_SLOT_DAC_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
#else
        .clk_cfg = I2S_PDM_TX_CLK_DEFAULT_CONFIG(EXAMPLE_PDM_TX_FREQ_HZ),
        /* The data bit-width of PDM mode is fixed to 16 */
        .slot_cfg = I2S_PDM_TX_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT, I2S_SLOT_MODE_MONO),
#endif
        .gpio_cfg = {
            .clk = EXAMPLE_PDM_TX_CLK_IO,
            .dout = EXAMPLE_PDM_TX_DOUT_IO,
            .invert_flags = {
                .clk_inv = false,
            },
        },
    };
    ESP_ERROR_CHECK(i2s_channel_init_pdm_tx_mode(tx_chan, &pdm_tx_cfg));

    /* Step 3: Enable the tx channel before writing data */
    ESP_ERROR_CHECK(i2s_channel_enable(tx_chan));

    return tx_chan;
}

void i2s_example_pdm_tx_task(void *args)
{
    int16_t *w_buf = (int16_t *)calloc(1, EXAMPLE_BUFF_SIZE);
    assert(w_buf);
    i2s_chan_handle_t tx_chan = i2s_example_init_pdm_tx();

    size_t w_bytes = 0;

    uint8_t cnt = 0;            // The current index of the song
    uint8_t tone_select = 0;    // To selecting the tone level

    printf("Playing %s `twinkle twinkle little star`\n", tone_name[tone_select]);
    while (1) {
        int tone_point = EXAMPLE_SINE_WAVE_LEN(tone[tone_select][song[cnt] - 1]);
        /* Generate the tone buffer */
        for (int i = 0; i < tone_point; i++) {
            w_buf[i] = (int16_t)((sin(2 * (float)i * CONST_PI / tone_point)) * EXAMPLE_WAVE_AMPLITUDE);
        }
        for (int tot_bytes = 0; tot_bytes < EXAMPLE_BYTE_NUM_EVERY_TONE * rhythm[cnt % 7]; tot_bytes += w_bytes) {
            /* Play the tone */
            if (i2s_channel_write(tx_chan, w_buf, tone_point * sizeof(int16_t), &w_bytes, 1000) != ESP_OK) {
                printf("Write Task: i2s write failed\n");
            }
        }
        cnt++;
        /* If finished playing, switch the tone level */
        if (cnt == sizeof(song)) {
            cnt = 0;
            tone_select++;
            tone_select %= 3;
            printf("Playing %s `twinkle twinkle little star`\n", tone_name[tone_select]);
        }
        /* Gap between the tones */
        vTaskDelay(15);
    }
    free(w_buf);
    vTaskDelete(NULL);
}
