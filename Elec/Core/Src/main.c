/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
typedef enum {
    MODE_OFF,
    MODE_LOW,
    MODE_MEDIUM,
    MODE_HIGH,
    MODE_AUTO,
    MODE_SINGLE
} Mode;
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define MAX_POSITION 1000


// Butonlar (LOW = basıldı)
#define BTN_OFF    (HAL_GPIO_ReadPin(Silecek_OFF_Butonu_GPIO_Port, Silecek_OFF_Butonu_Pin) == GPIO_PIN_RESET)
#define BTN_SINGLE (HAL_GPIO_ReadPin(Silecek_SINGLE_Butonu_GPIO_Port, Silecek_SINGLE_Butonu_Pin) == GPIO_PIN_RESET)
#define BTN_LOW    (HAL_GPIO_ReadPin(Silecek_LOW_Butonu_GPIO_Port, Silecek_LOW_Butonu_Pin) == GPIO_PIN_RESET)
#define BTN_MED    (HAL_GPIO_ReadPin(Silecek_MEDIUM_Butonu_GPIO_Port, Silecek_MEDIUM_Butonu_Pin) == GPIO_PIN_RESET)
#define BTN_HIGH   (HAL_GPIO_ReadPin(Silecek_HIGH_Butonu_GPIO_Port, Silecek_HIGH_Butonu_Pin) == GPIO_PIN_RESET)
#define BTN_AUTO   (HAL_GPIO_ReadPin(Silecek_AUTO_Butonu_GPIO_Port, Silecek_AUTO_Butonu_Pin) == GPIO_PIN_RESET)
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */

	// ===== FAR DURUMLARI =====
uint8_t A_KisaFar_F103_STS = 0;
uint8_t A_UzunFar_F103_STS = 0;

	// ===== SELEKTÖR =====
uint8_t A_Selektor_F103_STS = 0;

	// ===== SİNYAL SAYAÇLARI (INTERRUPT) =====
volatile uint8_t A_SolSinyalSayac_F103_VAL = 0;
volatile uint8_t A_SagSinyalSayac_F103_VAL = 0;
volatile uint8_t A_DortluSayac_F103_VAL    = 0;

	// ===== TIMER FLAG (SİNYAL SİSTEMİ)=====
volatile uint8_t A_SinyalTick_F103_TMP = 0;

	//========= SİLECEK SİSTEMİ ==============
Mode currentMode = MODE_OFF;
Mode requestedMode = MODE_OFF;

int position = 0;
int direction = 1;

bool pendingTransition = false;
bool singleActive = false;



/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
	// ==========FONKSİYONLAR=============
	// ========  FAR SİSTEMİ =============
void A_KisaFar_F103_Ctrl(void)
{
    if (HAL_GPIO_ReadPin(K_sa_Far_Butonu_GPIO_Port,
                          K_sa_Far_Butonu_Pin) == GPIO_PIN_RESET)
    {
        HAL_Delay(20);

        if (HAL_GPIO_ReadPin(K_sa_Far_Butonu_GPIO_Port,
                              K_sa_Far_Butonu_Pin) == GPIO_PIN_RESET)
        {
            A_KisaFar_F103_STS ^= 1;

            A_UzunFar_F103_STS = 0;
            HAL_GPIO_WritePin(Uzun_Far_Output_GPIO_Port,
                              Uzun_Far_Output_Pin,
                              GPIO_PIN_RESET);

            HAL_GPIO_WritePin(K_sa_Far_Output_GPIO_Port,
                              K_sa_Far_Output_Pin,
                              A_KisaFar_F103_STS ? GPIO_PIN_SET : GPIO_PIN_RESET);

            while (HAL_GPIO_ReadPin(K_sa_Far_Butonu_GPIO_Port,
                                    K_sa_Far_Butonu_Pin) == GPIO_PIN_RESET);
        }
    }
}


void A_UzunFar_F103_Ctrl(void)
{
    if (HAL_GPIO_ReadPin(Uzun_Far_Butonu_GPIO_Port, Uzun_Far_Butonu_Pin) == GPIO_PIN_RESET)
    {
        HAL_Delay(20); // debounce

        if (HAL_GPIO_ReadPin(Uzun_Far_Butonu_GPIO_Port, Uzun_Far_Butonu_Pin) == GPIO_PIN_RESET)
        {
            /* Uzun far toggle */
            A_UzunFar_F103_STS ^= 1;

            /* SADECE uzun farı kontrol et */
            HAL_GPIO_WritePin(Uzun_Far_Output_GPIO_Port,
                              Uzun_Far_Output_Pin,
                              A_UzunFar_F103_STS ? GPIO_PIN_SET : GPIO_PIN_RESET);

            while (HAL_GPIO_ReadPin(Uzun_Far_Butonu_GPIO_Port,
                                    Uzun_Far_Butonu_Pin) == GPIO_PIN_RESET);
        }
    }
}

void A_SolSinyal_F103_Ctrl(void)
{
    if (HAL_GPIO_ReadPin(Sol_Sinyal_Butonu_GPIO_Port,
                          Sol_Sinyal_Butonu_Pin) == GPIO_PIN_RESET)
    {
        HAL_Delay(20);

        if (HAL_GPIO_ReadPin(Sol_Sinyal_Butonu_GPIO_Port,
                              Sol_Sinyal_Butonu_Pin) == GPIO_PIN_RESET)
        {
            /* Override */
            A_SagSinyalSayac_F103_VAL = 0;
            A_DortluSayac_F103_VAL    = 0;
            HAL_GPIO_WritePin(Sa__Sinyal_Output_GPIO_Port,
                              Sa__Sinyal_Output_Pin,
                              GPIO_PIN_RESET);

            /* 5 kez yanıp sön = 10 toggle */
            A_SolSinyalSayac_F103_VAL = 10;

            while (HAL_GPIO_ReadPin(Sol_Sinyal_Butonu_GPIO_Port,
                                    Sol_Sinyal_Butonu_Pin) == GPIO_PIN_RESET);
        }
    }
}
void A_SagSinyal_F103_Ctrl(void)
{
    if (HAL_GPIO_ReadPin(Sa__Sinyal_Butonu_GPIO_Port,
                          Sa__Sinyal_Butonu_Pin) == GPIO_PIN_RESET)
    {
        HAL_Delay(20); // debounce

        if (HAL_GPIO_ReadPin(Sa__Sinyal_Butonu_GPIO_Port,
                              Sa__Sinyal_Butonu_Pin) == GPIO_PIN_RESET)
        {
            /* Override diğer sinyaller */
            A_SolSinyalSayac_F103_VAL = 0;
            A_DortluSayac_F103_VAL   = 0;

            HAL_GPIO_WritePin(Sol_Sinyal_Output_GPIO_Port,
                              Sol_Sinyal_Output_Pin,
                              GPIO_PIN_RESET);

            /* 5 kez yanıp sönme = 10 toggle */
            A_SagSinyalSayac_F103_VAL = 10;

            /* Buton bırakılana kadar bekle */
            while (HAL_GPIO_ReadPin(Sa__Sinyal_Butonu_GPIO_Port,
                                    Sa__Sinyal_Butonu_Pin) == GPIO_PIN_RESET);
        }
    }
}
void A_Dortlu_F103_Ctrl(void)
{
    if (HAL_GPIO_ReadPin(D_rtl__Butonu_GPIO_Port,
                          D_rtl__Butonu_Pin) == GPIO_PIN_RESET)
    {
        HAL_Delay(20); // debounce

        if (HAL_GPIO_ReadPin(D_rtl__Butonu_GPIO_Port,
                              D_rtl__Butonu_Pin) == GPIO_PIN_RESET)
        {
            /* Override sağ ve sol sinyal */
            A_SolSinyalSayac_F103_VAL = 0;
            A_SagSinyalSayac_F103_VAL = 0;

            /* 5 kez yanıp sönme = 10 toggle */
            A_DortluSayac_F103_VAL = 10;

            /* Buton bırakılana kadar bekle */
            while (HAL_GPIO_ReadPin(D_rtl__Butonu_GPIO_Port,
                                    D_rtl__Butonu_Pin) == GPIO_PIN_RESET);
        }
    }
}
void A_SinyalTickIsle_F103(void)
{
    if (!A_SinyalTick_F103_TMP) return;
    A_SinyalTick_F103_TMP = 0;

    if (A_DortluSayac_F103_VAL > 0)
    {
        HAL_GPIO_TogglePin(Sol_Sinyal_Output_GPIO_Port, Sol_Sinyal_Output_Pin);
        HAL_GPIO_TogglePin(Sa__Sinyal_Output_GPIO_Port, Sa__Sinyal_Output_Pin);
        A_DortluSayac_F103_VAL--;
    }
    else
    {
        if (A_SolSinyalSayac_F103_VAL > 0)
        {
            HAL_GPIO_TogglePin(Sol_Sinyal_Output_GPIO_Port, Sol_Sinyal_Output_Pin);
            A_SolSinyalSayac_F103_VAL--;
        }
        else
        {
            HAL_GPIO_WritePin(Sol_Sinyal_Output_GPIO_Port, Sol_Sinyal_Output_Pin, GPIO_PIN_RESET);
        }

        if (A_SagSinyalSayac_F103_VAL > 0)
        {
            HAL_GPIO_TogglePin(Sa__Sinyal_Output_GPIO_Port, Sa__Sinyal_Output_Pin);
            A_SagSinyalSayac_F103_VAL--;
        }
        else
        {
            HAL_GPIO_WritePin(Sa__Sinyal_Output_GPIO_Port, Sa__Sinyal_Output_Pin, GPIO_PIN_RESET);
        }
    }
}

void A_Selektor_F103_Ctrl(void)
{
    /* Uzun far butonla sabit açıksa, selektör devre dışı */
    if (A_UzunFar_F103_STS)
        return;

    /* Selektör basılı mı? (Pull-up, basınca RESET) */
    if (HAL_GPIO_ReadPin(Selekt_r_Butonu_GPIO_Port, Selekt_r_Butonu_Pin) == GPIO_PIN_RESET)
    {
        /* Uzun farı yak, kısa far ne durumdaysa kalsın */
        HAL_GPIO_WritePin(Uzun_Far_Output_GPIO_Port, Uzun_Far_Output_Pin, GPIO_PIN_SET);
        A_Selektor_F103_STS = 1;
    }
    else
    {
        /* Bırakıldıysa uzun farı kapat */
        if (A_Selektor_F103_STS)
        {
            HAL_GPIO_WritePin(Uzun_Far_Output_GPIO_Port, Uzun_Far_Output_Pin, GPIO_PIN_RESET);
            A_Selektor_F103_STS = 0;
        }
    }
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */
  HAL_TIM_Base_Start_IT(&htim2);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */
	  A_KisaFar_F103_Ctrl();
	  A_UzunFar_F103_Ctrl();
	  /* ===== SELEKTÖR ===== */
	  A_Selektor_F103_Ctrl();
	  /* ===== SİNYALLER ===== */
	  A_SolSinyal_F103_Ctrl();
	  A_SagSinyal_F103_Ctrl();
	  A_Dortlu_F103_Ctrl();
	  // ===== SİLECEK =====
	  handle_buttons();
	  motor_task();
    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 6399;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 2999;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_ENABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, K_sa_Far_Output_Pin|Uzun_Far_Output_Pin|Sol_Sinyal_Output_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, STEP_Pin|DIR_Pin|Sa__Sinyal_Output_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : B1_Pin */
  GPIO_InitStruct.Pin = B1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(B1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : D_rtl__Butonu_Pin Sol_Sinyal_Butonu_Pin */
  GPIO_InitStruct.Pin = D_rtl__Butonu_Pin|Sol_Sinyal_Butonu_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : K_sa_Far_Butonu_Pin Uzun_Far_Butonu_Pin Selekt_r_Butonu_Pin Silecek_OFF_Butonu_Pin
                           Silecek_SINGLE_Butonu_Pin Silecek_LOW_Butonu_Pin Silecek_MEDIUM_Butonu_Pin Silecek_HIGH_Butonu_Pin
                           Silecek_AUTO_Butonu_Pin */
  GPIO_InitStruct.Pin = K_sa_Far_Butonu_Pin|Uzun_Far_Butonu_Pin|Selekt_r_Butonu_Pin|Silecek_OFF_Butonu_Pin
                          |Silecek_SINGLE_Butonu_Pin|Silecek_LOW_Butonu_Pin|Silecek_MEDIUM_Butonu_Pin|Silecek_HIGH_Butonu_Pin
                          |Silecek_AUTO_Butonu_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : K_sa_Far_Output_Pin Uzun_Far_Output_Pin Sol_Sinyal_Output_Pin */
  GPIO_InitStruct.Pin = K_sa_Far_Output_Pin|Uzun_Far_Output_Pin|Sol_Sinyal_Output_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : Sa__Sinyal_Butonu_Pin */
  GPIO_InitStruct.Pin = Sa__Sinyal_Butonu_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(Sa__Sinyal_Butonu_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : STEP_Pin DIR_Pin Sa__Sinyal_Output_Pin */
  GPIO_InitStruct.Pin = STEP_Pin|DIR_Pin|Sa__Sinyal_Output_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2)
    {
    	A_SinyalTick_F103_TMP = 1;
    }
}

// ======= SİLECEK SİSTEMİ============


uint32_t get_delay()
{
    switch(currentMode)
    {
        case MODE_LOW:    return 5;   // yavaş
        case MODE_MEDIUM: return 3;   // orta
        case MODE_HIGH:   return 1;   // hızlı
        case MODE_AUTO:   return 3;   // şimdilik MEDIUM
        default: return 0;
    }
}

void handle_buttons()
{
    if(BTN_LOW) {
        currentMode = MODE_LOW;
        pendingTransition = false;
    }
    else if(BTN_MED) {
        currentMode = MODE_MEDIUM;
        pendingTransition = false;
    }
    else if(BTN_HIGH) {
        currentMode = MODE_HIGH;
        pendingTransition = false;
    }
    else if(BTN_OFF) {
        requestedMode = MODE_OFF;
        pendingTransition = true;
    }
    else if(BTN_AUTO) {
        requestedMode = MODE_AUTO;
        pendingTransition = true;
    }
    else if(BTN_SINGLE) {
        requestedMode = MODE_SINGLE;
        pendingTransition = true;
    }
}

void apply_transition_if_ready()
{
    if(pendingTransition && position == 0 && direction == -1)
    {
        pendingTransition = false;

        if(requestedMode == MODE_OFF)
        {
            currentMode = MODE_OFF;
        }
        else if(requestedMode == MODE_AUTO)
        {
            currentMode = MODE_AUTO;
        }
        else if(requestedMode == MODE_SINGLE)
        {
            currentMode = MODE_SINGLE;
            singleActive = true;
            direction = 1;
        }
    }
}

void check_single_done()
{
    if(currentMode == MODE_SINGLE && singleActive)
    {
        if(position == 0 && direction == -1)
        {
            currentMode = MODE_OFF;
            singleActive = false;
        }
    }
}

void motor_task()
{
    if(currentMode == MODE_OFF)
    {
        return;
    }

    if(position >= MAX_POSITION)
    {
        position = MAX_POSITION;
        direction = -1;
    }
    else if(position <= 0)
    {
        position = 0;
        direction = 1;
    }

    // YÖN AYARI
    HAL_GPIO_WritePin(DIR_GPIO_Port, DIR_Pin,
        (direction == 1) ? GPIO_PIN_SET : GPIO_PIN_RESET);

    // STEP PULSE
    HAL_GPIO_WritePin(STEP_GPIO_Port, STEP_Pin, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(STEP_GPIO_Port, STEP_Pin, GPIO_PIN_RESET);
    HAL_Delay(1);

    if(direction == 1) position++;
    else position--;

    apply_transition_if_ready();
    check_single_done();

    HAL_Delay(get_delay());
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
