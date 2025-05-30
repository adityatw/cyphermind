## Example Prompts

### Prompt for Cypher query generation
<p>
With the following node labels: Company, Speaker, Session, TimeSlot, Room, Track, and relationship types: REPRESENTS, SPEAKS_AT, LOCATED_IN, SCHEDULED_AT, PART_OF, please write a Cypher query that summarizes all relationships for the Track named 'GraphRAG (08)'. Use the relationship types exactly as written (case-sensitive). Assume relationship direction may not be consistently enforced, so use undirected relationships unless the logic clearly requires direction. The field name in the Timeslot node is datetime. Output only valid Cypher in a format that can be directly passed into a Neo4j Cypher Reader node,without markdown formatting or triple backticks, explanations or comments.

### Prompt for Summarization
<p>
Based on the query result, generate a summary in under 300 words that describes the track, company, presenter, and session title. Write in well-formed sentences. Do not leave any sentence unfinished. End with a complete closing sentence that summarizes the key takeaway. The last sentence in the summary has to end with a period. 