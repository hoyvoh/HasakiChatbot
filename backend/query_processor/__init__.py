'''
2. Task Determination Using MiniLM
Functionality: MiniLM analyzes the query and determines the specific task required (product details, pricing, promotion, recommendations, comparison, reviews, assurance/return policy, web page routing, stock availability).
Inputs: User query.
Output: Task type and relevant product term(s), signals, or budget range depending on the user's request.

3. Product Details Retrieval
Flow:
MiniLM identifies product-related queries and returns the product term.
Preprocess and embed the product term for search.
Search product by title in a vector database and return the product ID.
Query SQL DB for all metadata by product ID.
Construct a prompt that includes:
Product information.
Guide for structuring the answer.
User query.
Output: Detailed product information prompt sent to LLM for response generation.

4. Pricing and Promotion Information Retrieval
Flow:
MiniLM identifies pricing or promotion-related queries.
Preprocess and embed the product term.
Search product by title in vectorDB and return the product ID.
Query SQL DB for pricing and promotion details.
Query promotion documents for related info.
Construct a prompt that includes:
Product pricing details.
Promotion information and links.
Guide for structuring the answer.
User query.
Output: Pricing and promotion details sent to LLM.

5. Product Recommendations Based on User Needs and Budget
Flow:
MiniLM extracts product term and budget range from the query.
Search in vectorDB by product title and description to get top 10 product IDs.
Query SQL DB for products within the specified price range.
Construct a prompt that includes:
Product recommendations.
Guide for structuring the answer.
User query.
Output: Product recommendations sent to LLM.

6. Product Comparison
Flow:
MiniLM extracts two or more product terms from the query.
Preprocess and embed product terms.
Query vectorDB for relevant product IDs.
Query SQL DB for product metadata.
Construct a prompt that includes:
Comparison of products.
Guide for structuring the answer.
User query.
Output: Product comparison details sent to LLM.

7. Product Reviews and Ratings Retrieval
Flow:
MiniLM identifies queries about reviews or ratings.
Preprocess and embed product term.
Query vectorDB and retrieve product ID.
Query SQL DB for review summaries and ratings.
Construct a prompt that includes:
Product reviews and ratings.
Guide for structuring the answer.
User query.
Output: Reviews and ratings information sent to LLM.

8. Assurance and Return Policy Information
Flow:
MiniLM detects queries related to assurance or return policies.
Preprocess and embed the query.
Query the document vectorDB for relevant assurance or return policy documents.
Construct a prompt that includes:
Assurance and return policy details.
Guide for structuring the answer.
User query.
Output: Assurance/return policy information sent to LLM.

9. Web Page Routing Information
Flow:
MiniLM identifies queries about web page routing.
Preprocess and embed the page terms from the query.
Query vectorDB of web documents for the routing information.
Construct a prompt that includes:
Routing details.
Guide for structuring the answer.
User query.
Output: Web page routing information sent to LLM.
'''