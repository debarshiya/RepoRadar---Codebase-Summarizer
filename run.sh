#!/bin/bash
export $(cat .env | xargs)
streamlit run src/app.py