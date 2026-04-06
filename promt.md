make a web app to write wordpress posts using AI.
The ui will have menu column on the left and the main board on the right.
In the menu board will have these tabs:
- General: which will show how many jobs are running, how many jobs are waiting, how many jobs are completed, how many jobs are failed.
- Settings: which will have these sub-category:
+ AI Providers: where user add their AI provider API keys. It will support OpenAI, Gemini, and Anthropic.
+ wordpress sites: where user add their wordpress sites using api keys. User will provide site name, site url and site API key. It will support multiple sites.
- Projects: which will have list of projects. Each project will have a title, description, and a specific Wordpress site which is added before. Make a button to create a project which will open a modal to input the project title, description, and select a wordpress site.

In each project, there will be some sub tabs:
- General: show how many posts are published, how many posts are waiting for approve, how many posts are failed, how many posts are draft.
- Content: which will have a list of posts. Each post will have a title, thumbnail, research: boolean, true when this post is researched, status, content (true/false), true when the post have more than 4k words, Thump: boolean, true when the post have a thumbnail, Section: boolean, true when the post have a section, and a button to view the post, a button to remove the post, public/unpublish post button.

There will be create post button, that open a box and show these section:
- Single post: user will provide a topic and an additional requests. The tool will do these steps:
+ Research the topic using AI provider.
This step will reseach to find the audience of the topic, the keywords for the topics, and the answer need to be provided. It also find points to mention in the post.
+ Make an outline for the post.
Make a SEO optimized title for this post.
Write a meta Descrtiption
In the introduce of the article, write 3 parts: Hook, problem and Promise
Generate a section for each point. Each section will have a title and a content.
+ generate content for the post
Generate content for each section. Each section will have a title and a content.
+ Create thumbnail: user will have 2 options: generate or upload. If generate, use AI to generate a thumbnail.
+ Generate a section picture: user will have 2 options: generate or upload. If generate, use AI to generate a section picture.
+ Post to wordpress site. This will provide a preview of the post before publishing and the token usage for each step.
Each of this is a job, and can be done in parallel.

- Bulk post: user will provide a list of topics and an additional requests. The tool will create multiple jobs for each topic and do the same steps as single post.

Technical:
- The backend need to be written in FastAPI. The frontend need to be written in React.
- For the database, use mongodb.
- Use redis for caching and job queue.
- Use docker to containerize the application, make a docker compose for each component of this service

