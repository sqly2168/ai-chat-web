My goal is a project in linux with an online chatbot which connects to a language model and answers me with a specific behaviour.
I want to make my website first.
I downloaded https://huggingface.co/google/gemma-3-12b-pt gguf in llama/models folder
since the model is working fine i'll need the backend and the frontend to be connected --Python flask
I finished the backend, and created a basic ui with a conversation box and a chatbox on the frontend with js

#first version done.
#----------------------------------------------------------------------------
User types a message
-JS sends POST /chat with JSON
-Flask receives it
-Backend runs gemma
-Model returns response
-Flask sends JSON response
-JS displays the reply

#conclusion
problem: every msg the model is restarted, loaded, gives a response and unloads.
I"ll need to:
    stream the model, 
    use it on websocket like chatgpt,
    then optimize the gpu
    and finally give it system prompt, personaliy, memory
I'll need to take some time and understand this version before moving to next version.






#----------------------------------------------------------------------------
#V2 stream the model - use flask-socketio extension
#----------------------------------------------------------------------------





Due to many problems with:
    -stdout buffering
    -subprocess deadlock
    -treading/eventlet conflict
I decided to move forward with a different approach:
Instead of running the model directly through a subprocess (llama-cli) and manually parsing its stdout output, I switched to using the llama.cpp HTTP server (llama-server).