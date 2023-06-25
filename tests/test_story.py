from storylord import StoryLord

def test_story():
    story_prompt = "A medicore developer writes tests for his story generation project"
    lord = StoryLord()
    lord.create_storybook(story_prompt)