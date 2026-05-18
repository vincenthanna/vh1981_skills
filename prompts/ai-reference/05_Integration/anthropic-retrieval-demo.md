---

Claude Search and Retrieval Demo [Experimental]
소개
Anthropic Python SDK를 사용하여 다양한 knowledge base(Elasticsearch, 벡터 데이터베이스, 웹 검색, Wikipedia)에서 Claude의 Search and Retrieval 기능을 실험해보는 경량 데모이다. 이 데모에서는 전통적인 retrieval-augmented generation (RAG) 기법의 대안을 탐구한다.
Repository는 다음 디렉터리를 포함한다:

Directory
Description

claude_retriever
Claude의 API를 사용하는 핵심 search 및 retrieval 로직 포함.

examples
다양한 검색 도구로 claude_retriever를 사용하는 방법을 보여주는 예제 notebook 및 script 제공.

tests
embedder, util, search tool에 대한 unit 및 integration 테스트 포함.

목차

Setup

General Environment Variables

How it works

Explanation of core methods
A peek under the hood

Examples

Wikipedia Search
Vector Database Search
Web Search (Brave)
Enterprise Search (Elasticsearch)

Setup
이 retrieval 데모는 Python 3.10을 사용한다. 아직 없다면 설치하라.
Repository를 clone한다:
git clone https://github.com/anthropic/claude-retriever-demo.git

데모 디렉터리로 이동한다:
cd claude-retriever-demo

가상 환경 사용을 권장한다. 생성하고 활성화한다:
python3 -m venv venv
source venv/bin/activate

데모를 설치한다:
pip install -e .

conda 또는 다른 가상 환경 관리자를 사용하는 경우, repo를 clone한 후 새 환경을 생성한다:
conda create --name retrieval
conda activate retrieval

requirement를 설치한다:
conda install pip 
pip install -r requirements.txt

General Environment Variables
최소한 다음 환경 변수를 추가해야 한다:

Environment Variable
Description

ANTHROPIC_API_KEY
Anthropic의 Claude에 대한 API key. 여기에서 API key를 신청할 수 있다.

설정이 완료되면 /examples의 예제 notebook을 참조하여 retrieval workflow 테스트를 시작한다.
Usage
높은 수준에서, Retrieval Demo는 다음과 같이 작동한다:

자연어 query를 받아 형식화된 검색 결과를 반환할 수 있는 SearchTool 객체를 설정한다.
ClientWithRetrieval 객체를 초기화한다. 이는 base Anthropic SDK의 Client 객체를 상속한다. SearchTool 객체를 받는다.
completion_with_retrieval 메서드를 통해 retrieval을 수행한다. 이는 base completion 메서드와 유사하지만, Claude가 query를 발행하고 SearchTool을 사용하여 주어진 task를 더 잘 해결한다. retrieval을 실험하는 가장 빠른 방법이다.

또한 completion_with_retrieval 내에서 사용되며 standalone으로도 사용 가능한 두 가지 메서드를 제공한다:

retrieve: retrieve 메서드는 주어진 question task에 대해 Claude가 관련 정보를 수집하도록 단일 호출을 수행할 수 있게 한다. 이는 검색 결과를 downstream에서 사용하고 추가적인 후처리를 적용할 수 있게 함으로써 RAG pipeline의 steerability를 더 크게 제공한다.
answer_with_results: answer_with_results 메서드는 전통적인 retrieval-augmented generation 단계를 수행하며, 검색 결과를 context로 하여 Claude가 query에 대한 답변을 제공하도록 한다.

핵심 메서드 설명
answer_with_results()
이 메서드는 오늘날 대부분의 RAG pipeline에서 전통적인 합성 단계에 해당한다. 여기서는 Claude에게 검색 결과를 제공하고 사용자 질문에 대한 답변을 합성하도록 요청한다.

다음 단계를 통해 작동한다:

사용자의 질문과 검색 결과가 메서드에 전달된다.
format_search_results 매개변수가 True로 설정된 경우, Claude가 기대하도록 fine-tuning된 형식으로 검색 결과를 재포맷한다.
형식화된 검색 결과와 원래 질문이 Claude에 전달되어 completion을 생성한다.
Claude는 검색 결과를 읽고 관련 정보를 추출하여 사용자 질문에 대한 답변을 합성한다.
Claude가 생성한 답변이 반환된다.

전통적인 RAG pipeline에 Claude를 통합하려면 answer_with_results() 메서드를 단독으로 호출할 수 있다. format_search_results 매개변수를 True로 설정하고 원시 검색 결과 리스트(list[str] 형태)를 메서드에 전달한다.
retrieve()
전통적인 RAG pipeline은 knowledge base에서 검색 결과가 수집된 후에만 답변을 위해 LLM을 사용한다. retrieve() 메서드는 프로세스 초기에 Claude의 기능을 활용한다.
retrieve()는 Claude가 질문에 답하기에 충분한 정보가 수집되었다고 판단할 때까지 knowledge base를 반복적으로 검색하여 관련 정보를 수집할 수 있게 한다. 이러한 접근 방식을 통해 Claude를 사용하여 초기 사용자 질문만을 검색 query로 사용하는 것보다 더 관련성 있는 정보를 수집할 수 있다.

다음은 흐름이다:

원래 query가 Claude에 전달된다.
Claude는 원래 query를 기반으로 자연어 검색 query를 생성한다.
검색이 search tool에 전달된다. document가 반환된다.
Claude가 검색 결과를 받는다.
Claude는 충분한 정보가 수집되었는지 평가한다.
Claude는 max_searches_to_try까지 검색을 계속한다.
완료되면 최종 검색 결과 집합이 정리(중복 제거, 형식화)되어 반환된다.

retrieve()가 최종 답변이 아닌 검색 결과를 반환한다는 점에 유의해야 한다. 이는 결과에 대한 추가적인 downstream 처리를 가능하게 한다. 모듈식 구조는 검색 프로세스에 대해 더 많은 제어를 제공한다.
Search tool
search tool은 자연어 query를 받아 information source에서 query와 관련된 결과를 반환한다.

데모는 일반적인 search tool의 예제를 포함한다:

웹 검색 (Brave 사용, 웹의 최신 정보로 Claude 보강)
Wikipedia 검색 (전체 knowledge base로 Claude 보강)
Embedding 검색 (Pinecone 또는 로컬을 통해, 임의의 데이터셋의 chunk로 Claude 보강)
Enterprise 검색 (ElasticSearch를 통해, 임의의 데이터셋의 전체 document로 Claude 보강)

/searcher/searchtools/ 폴더에 도구를 위한 새 Python 파일을 생성하여 데모에 새로운 SearchTool을 쉽게 추가할 수 있다.
completion_with_retrieval()

ClientWithRetrieval 메서드 completion_with_retrieval()는 retrieve와 answer_with_results 메서드를 결합한다. 다음 단계를 통해 작동한다:

사용자의 원래 질문이 query로 Claude에 전달된다.
retrieve 메서드가 호출되고 Claude가 관련 검색 결과 수집을 시작한다.
retrieve가 관련 검색 결과를 반환한다.
검색 결과와 사용자의 원래 질문이 answer_with_results 메서드에 전달된다.
answer_with_results가 검색 결과 내의 정보를 사용하여 질문에 답변한다.
최종 답변이 사용자에게 반환된다.

Retrieval Under the Hood
이전 섹션의 예제를 사용하여 Retrieval Demo를 사용할 때 Claude의 실제 응답과 출력이 어떻게 보이는지 살펴보자.
다음 메서드를 실행한다고 가정한다:
client = ClientWithRetrieval(api_key=os.environ['ANTHROPIC_API_KEY'], search_tool=amazon_products_search_tool)

augmented_response = client.completion_with_retrieval(
    query="I want to get my daughter more interested in science. What kind of gifts should I get her?",
    model=ANTHROPIC_MODEL,
    n_search_results_to_use=3,
    max_searches_to_try=5,
    max_tokens_to_sample=1000)

query는 Claude에게 검색 task와 사용 가능한 search tool에 대해 지시하는 template에 추가된다. Claude는 이 prompt를 읽고 검색을 수행해야 함을 이해한다.
Claude는 초기 검색 query를 작성하고 출력한다:
<search_query>science gifts</search_query>

client에서 실행되는 데모 코드는 검색어 "science gifts"를 추출하고 연결된 search tool을 호출한다. 도구는 결과를 반환하며, 이는 <search_results> 태그 사이에 추가된다:
<search_results>
<item index="1">
<page_content>
Product Name: LeapFrog Dino's Delightful Day Alphabet Book, Green

About Product: Letters and words are woven into the story in alphabetical order with phonetic sounds to introduce ABCs to your little one through a charming tale | Flip through the 16 interactive pages to hear the story read aloud, or enjoy musical play by jamming to a melody with fun sounds and musical notes | Press the light-up button to hear letter names, letter sounds and words from the story | Number buttons along Dino's back introduce counting and recognizing numbers from one to ten | This complete story with beginning, middle and end exposes your child to early reading skills. 2AA batteries are included for demo purposes, replace new batteries for regular use. Product dimensions: 12.3" Wide x 12.5" Height x 2.7" Depth

Categories: Toys & Games | Learning & Education | Science Kits & Toys
</page_content>
</item>
<item index="2">
<page_content>
Product Name: Tiger Tribe Dinosaurs Colouring Set

About Product: Small book, big fun; explore the Prehistoric world of dinosaurs as you use the 10 vibrantly colored markers to color in and design your favorite dynos | Beautifully illustrated coloring set Jam packed with markers, stickers, and coloring pages, all in a perfectly portable package | Contains a 48-page coloring book, 10 high quality markers, 5 sticker sheets and two special storage drawers to stash your stuff | Cleverly designed book-like box has compartments to keep everything neat and organized; innovative magnet closure keeps it all together | For boys and girls ages 3+

Categories: Toys & Games | Arts & Crafts
</page_content>
</item>
</search_results>

이는 원본 prompt와 Claude의 <search_query> 출력에 추가된다. max_searches_to_try에 도달할 때까지 이 프로세스가 반복된다. 마지막으로 Claude는 제공된 <search_results>를 사용하여 최종 답변을 생성한다.
Examples
모든 검색 통합의 예제는 이 Colab에 있다.
Search API를 사용하여 Wikipedia 접근하기
이 예제는 examples/ 폴더에서 볼 수 있다.
Claude를 Wikipedia의 모든 지식으로 보강하는 방법을 보여주기 위해 WikipediaSearchTool을 미리 정의했다:
from claude_retriever.searcher.searchers import WikipediaSearchTool

wikipedia_search_tool = WikipediaSearchTool()
client = claude_retriever.ClientWithRetrieval(api_key=os.environ['ANTHROPIC_API_KEY'],
                                              search_tool = wikipedia_search_tool)

query = "Do NBA players typically get the recommended amount of sleep for adults?"

# get the search results that can be use to answer a query:
search_results = client.retrieve(
    query=query,
    stop_sequences=[anthropic.HUMAN_PROMPT, "END_OF_SEARCH"],
    model="claude-2.0",
    n_search_results_to_use=1, # Use only the top search result, so Claude can adapt queries quickly
    max_searches_to_try=3, # Reducing this number will make the search process faster, but less likely to get the best results
    max_tokens_to_sample=1000)

# or get Claude's answer informed by the search results:
answer = client.completion_with_retrieval(
    prompt=prompt,
    model="claude-2.0",
    n_search_results_to_use=1, # Get a single result each time so Claude can quickly adapt its searches
    max_searches_to_try=3, # Increasing this number allows Claude to run more searches as it looks for information
    max_tokens_to_sample=1000)
Embedding 데이터베이스 설정 및 사용
이 예제는 examples/ 폴더에서 로컬 vectorstore를 사용하는 것을 볼 수 있다.
이 예제는 examples/ 폴더에서 원격 vectorstore를 사용하는 것을 볼 수 있다.
일반적인 외부 knowledge base는 document 집합이다. 이 예제에서는 로컬 document를 chunk하고 embed하여 (로컬) vectorstore에 저장한 다음, query에 답할 때 해당 vectorstore에서 retrieve한다.
VectorStore와 SearchTool 설정
# Create a vector store and populate it with documents
from claude_retriever.searcher.vectorstores.local import LocalVectorStore
from claude_retriever.utils import embed_and_upload

input_file = "documents_to_embed.jsonl" # Each line of this file should be a JSON object with a "text" field
disk_path = "local_vector_store.jsonl" # The vector store will be saved to this file
vector_store = LocalVectorStore(disk_path=disk_path)
embed_and_upload(input_file, vector_store, tokens_per_chunk=384, batch_size=128)

# Create a search tool for the vector store
from claude_retriever.searcher.searchers import EmbeddingSearchTool

tool_description='The search engine will search over the Test database, and return for each product its title, description, and a set of tags.' # This provides instructions to Claude on how to use the search tool
search_tool = EmbeddingSearchTool(
    tool_description=tool_description,
    vector_store=vector_store
)
EmbeddingSearchTool 사용하기
client = claude_retriever.ClientWithRetrieval(api_key=os.environ['ANTHROPIC_API_KEY'],
                                              search_tool = search_tool)

query = "I want to get my daughter more interested in science. What kind of gifts should I get her?"

# get the search results that can be use to answer a query:
search_results = client.retrieve(
    query=query,
    stop_sequences=[anthropic.HUMAN_PROMPT, "END_OF_SEARCH"],
    model="claude-2.0",
    n_search_results_to_use=1, # Use only the top search result, so Claude can adapt queries quickly
    max_searches_to_try=3, # Reducing this number will make the search process faster, but less likely to get the best results
    max_tokens_to_sample=1000)

# or get Claude's answer informed by the search results:
answer = client.completion_with_retrieval(
    query=query,
    model="claude-2.0",
    n_search_results_to_use=1, # Get a single result each time so Claude can quickly adapt its searches
    max_searches_to_try=3, # Increasing this number allows Claude to run more searches as it looks for information
    max_tokens_to_sample=1000)
BraveSearchTool로 인터넷 검색하기
이 예제는 examples/ 폴더에서 볼 수 있다.
Retrieval을 통해 Claude는 이제 BraveSearchTool을 사용하여 인터넷에 접근할 수 있다. Brave API key만 제공하면 된다 (여기에서 계정을 등록할 수 있다). 다음은 BraveSearchTool을 사용하는 예제이다:
from claude_retriever.searcher.searchtools.websearch import BraveSearchTool

# Create a searcher
brave_search_tool = BraveSearchTool(brave_api_key=os.environ["BRAVE_API_KEY"], summarize_with_claude=True, anthropic_api_key=os.environ["ANTHROPIC_API_KEY"])

client = claude_retriever.ClientWithRetrieval(api_key=os.environ['ANTHROPIC_API_KEY'],
                                              search_tool = search_tool)

query = "I want to get my daughter more interested in science. What kind of gifts should I get her?"

# get the search results that can be use to answer a query:
search_results = client.retrieve(
    query=query,
    stop_sequences=[anthropic.HUMAN_PROMPT, "END_OF_SEARCH"],
    model="claude-2.0",
    n_search_results_to_use=1, # Use only the top search result, so Claude can adapt queries quickly
    max_searches_to_try=3, # Reducing this number will make the search process faster, but less likely to get the best results
    max_tokens_to_sample=1000)

# or get Claude's answer informed by the search results:
answer = client.completion_with_retrieval(
    query=query,
    model="claude-2.0",
    n_search_results_to_use=1, # Get a single result each time so Claude can quickly adapt its searches
    max_searches_to_try=3, # Increasing this number allows Claude to run more searches as it looks for information
    max_tokens_to_sample=1000)
Elasticsearch를 search tool로 사용하기
이 예제는 examples/ 폴더에서 로컬 vectorstore를 사용하는 것을 볼 수 있다.
Claude를 이용한 Retrieval은 ElasticsearchCloudSearchTool을 통해 Elasticsearch도 지원한다. 다음은 Amazon 제품 목록 데이터를 포함하는 index에 대해 생성된 search tool을 사용하는 예제이다:
from claude_retriever.searcher.searchtools.elasticsearch import ElasticsearchCloudSearchTool

AMAZON_SEARCH_TOOL_DESCRIPTION = 'The search engine will search over the Amazon Product database, and return for each product its title, description, and a set of tags.'
amazon_search_tool = ElasticsearchCloudSearchTool(tool_description=AMAZON_SEARCH_TOOL_DESCRIPTION,
                                                  elasticsearch_cloud_id=cloud_id,
                                                  elasticsearch_api_key_id=api_key_id,
                                                  elasticsearch_api_key=api_key,
                                                  elasticsearch_index=index_name)

client = claude_retriever.ClientWithRetrieval(api_key=os.environ['ANTHROPIC_API_KEY'],
                                              search_tool = search_tool)

query = "I want to get my daughter more interested in science. What kind of gifts should I get her?"

# get the search results that can be use to answer a query:
search_results = client.retrieve(
    query=query,
    stop_sequences=[anthropic.HUMAN_PROMPT, "END_OF_SEARCH"],
    model="claude-2.0",
    n_search_results_to_use=1, # Use only the top search result, so Claude can adapt queries quickly
    max_searches_to_try=3, # Reducing this number will make the search process faster, but less likely to get the best results
    max_tokens_to_sample=1000)

# or get Claude's answer informed by the search results:
answer = client.completion_with_retrieval(
    query=query,
    model="claude-2.0",
    n_search_results_to_use=1, # Get a single result each time so Claude can quickly adapt its searches
    max_searches_to_try=3, # Increasing this number allows Claude to run more searches as it looks for information
    max_tokens_to_sample=1000)
Elasticsearch API key 설정과 document를 Elasticsearch에 업로드하는 방법에 대한 가이드는 Retrieval explainer doc도 참조하라.
