---
title: workflow
---
flowchart TD
	DRIVERA--step1-->speak_detection--step2-->message_formatting--step3-->voice_generator--step4-->DRIVERA--step5-->speak_detection--step6-->LLM_check--False-->DRIVERA
	LLM_check--True-->json_send-->message_deformating-->voice_generator-->DRIVERB
