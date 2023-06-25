# StoryLord: Children's Book Generator

# Example
```
from storylord import StoryLord

story_prompt = "A turtle journeys into outer space to find signs of extraterrestrial life"
    
lord = StoryLord()
lord.create_storybook(story_prompt)
```

# Requirements
OpenAI API Key needs to be provided to the `StoryLord` class by either:
- setting the `OPENAI_API_KEY` env. variable (preferred)
- setting the `openai_api_key` kwarg 

# Development
`tox -e dev && source .tox/dev/bin/activate`

# Testing
`tox`