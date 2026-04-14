/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define B1_Pin GPIO_PIN_13
#define B1_GPIO_Port GPIOC
#define B1_EXTI_IRQn EXTI15_10_IRQn
#define D_rtl__Butonu_Pin GPIO_PIN_0
#define D_rtl__Butonu_GPIO_Port GPIOC
#define Sol_Sinyal_Butonu_Pin GPIO_PIN_1
#define Sol_Sinyal_Butonu_GPIO_Port GPIOC
#define K_sa_Far_Butonu_Pin GPIO_PIN_0
#define K_sa_Far_Butonu_GPIO_Port GPIOA
#define Uzun_Far_Butonu_Pin GPIO_PIN_1
#define Uzun_Far_Butonu_GPIO_Port GPIOA
#define Selekt_r_Butonu_Pin GPIO_PIN_4
#define Selekt_r_Butonu_GPIO_Port GPIOA
#define K_sa_Far_Output_Pin GPIO_PIN_5
#define K_sa_Far_Output_GPIO_Port GPIOA
#define Uzun_Far_Output_Pin GPIO_PIN_6
#define Uzun_Far_Output_GPIO_Port GPIOA
#define Sol_Sinyal_Output_Pin GPIO_PIN_7
#define Sol_Sinyal_Output_GPIO_Port GPIOA
#define Sa__Sinyal_Butonu_Pin GPIO_PIN_0
#define Sa__Sinyal_Butonu_GPIO_Port GPIOB
#define STEP_Pin GPIO_PIN_12
#define STEP_GPIO_Port GPIOB
#define DIR_Pin GPIO_PIN_13
#define DIR_GPIO_Port GPIOB
#define Silecek_OFF_Butonu_Pin GPIO_PIN_8
#define Silecek_OFF_Butonu_GPIO_Port GPIOA
#define Silecek_SINGLE_Butonu_Pin GPIO_PIN_9
#define Silecek_SINGLE_Butonu_GPIO_Port GPIOA
#define Silecek_LOW_Butonu_Pin GPIO_PIN_10
#define Silecek_LOW_Butonu_GPIO_Port GPIOA
#define Silecek_MEDIUM_Butonu_Pin GPIO_PIN_11
#define Silecek_MEDIUM_Butonu_GPIO_Port GPIOA
#define Silecek_HIGH_Butonu_Pin GPIO_PIN_12
#define Silecek_HIGH_Butonu_GPIO_Port GPIOA
#define TMS_Pin GPIO_PIN_13
#define TMS_GPIO_Port GPIOA
#define TCK_Pin GPIO_PIN_14
#define TCK_GPIO_Port GPIOA
#define Silecek_AUTO_Butonu_Pin GPIO_PIN_15
#define Silecek_AUTO_Butonu_GPIO_Port GPIOA
#define SWO_Pin GPIO_PIN_3
#define SWO_GPIO_Port GPIOB
#define Sa__Sinyal_Output_Pin GPIO_PIN_6
#define Sa__Sinyal_Output_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
