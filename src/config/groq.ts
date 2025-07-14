import Groq from 'groq-sdk'

export const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
})

export const GROQ_MODEL = 'llama3-70b-8192'
export const MAX_TOKENS = 1024
export const TEMPERATURE = 1
