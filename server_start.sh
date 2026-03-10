#!/bin/bash
/home/sqly/Llama/llama.cpp/build/bin/llama-server \
  -m /home/sqly/Llama/models/google_gemma-3-12b-it-Q4_K_M.gguf \
  -ngl 99 -c 4096 --port 8080
