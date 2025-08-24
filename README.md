Project goal:
- take duo security logs from duo application
- use tensorflow to identify frauds that are serious after training on X amount of data.
-before doing anything contact use using text or ai voice
- take action (lock out,dismiss,mark suspicious etc.)


goal of the project is to simplify the triage through Duo's offered api services



****UPDATE
tensor flow will be pushed back and substituted with rule based approach temporarily.



***READ
(due to ngrok free tier Make file will not work as twilio forwarding url is hardcoded and changes each
restart requiring you to go into twilio to manually change the url.)


1.run ngrok http 5003
2.copy forwarding link (ending with .app) and paste it into develop>manage>active numbers>your active number link (ex: 341-111-1111)> paste in url filter {https://91abd523f28d.ngrok-free.app/incoming-call} or it will drop.
2.run  python3 twilio_agent.py
3.run python3 init.py


