Stable Diffusion Discord Bot

REQUIREMENTS:

Python
CUDA Enabled GPU
Discord Bot Token (https://discord.com/developers/applications)


To get started with the program all you need to do is open up the "WebUI.bat" file in the folder, which will initiate the Stable Diffusion WebUI. It will prompt you to download a stable diffusion checkpoint. The most recent checkpoint is located here:
https://huggingface.co/runwayml/stable-diffusion-v1-5/blob/main/v1-5-pruned.ckpt
Just download v1-5-pruned.ckpt or v1-5-pruned-emaonly.ckpt Place the downloaded file in stable-diffusion-webui > models > Stable-diffusion Run WebUI.bat again and once it says "Running on local URL: http://127.0.0.1:7860" that part is done.

Next, shift-right click in the folder and click "Open Powershell window here". Then run the following command: python app.py "TOKEN" Ensure you keep the " and replace TOKEN with your bot's token.


Thank you to AUTOMATIC1111's stable diffusion webui, without it this would not be possible.