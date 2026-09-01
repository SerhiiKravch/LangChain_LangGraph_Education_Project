# AI Support Inbox Agent

Навчальний pet-project для практики `LangChain` і `LangGraph` на реалістичному, але компактному сценарії. Проєкт імітує AI-асистента для support inbox: він приймає вхідне звернення клієнта, знаходить релевантні документи в базі знань, готує чернетку відповіді, оцінює ризик дії та або відправляє відповідь автоматично, або зупиняється на кроці human review.

Цей проєкт задуманий не як “ще один чат з LLM”, а як маленька production-style система, де можна попрактикувати:

- `LangChain` для моделей, prompts, tools, structured output і RAG.
- `LangGraph` для stateful orchestration, branching, retries, interrupts і resume.
- Побудову безпечного agent workflow з human-in-the-loop.
- Production-мислення: observability, error handling, idempotency, тестування.

## Ціль проєкту

Мета проєкту: збудувати невеликий агентний workflow, який покриває типові питання зі співбесіди по `LangChain` / `LangGraph` не лише теоретично, а й практично.

Після реалізації ти зможеш впевнено пояснити:

- коли достатньо `LangChain`, а коли варто використовувати `LangGraph`;
- як працюють `State`, `Node`, `Edge` та `StateGraph`;
- як будувати RAG-пайплайн;
- як додавати tools до агента;
- як реалізувати human-in-the-loop через interrupt/resume;
- як організувати retries, checkpointing і persistence;
- як зменшувати hallucinations і контролювати ризиковані дії;
- як тестувати agent workflow на практиці.

## Ідея продукту

Система обробляє support tickets або email-звернення від користувачів. Для кожного звернення вона має:

1. Прийняти вхідний текст.
2. Визначити категорію запиту.
3. Знайти релевантні документи в knowledge base.
4. Підготувати grounded draft response.
5. Оцінити, чи безпечно відповісти автоматично.
6. Якщо ризик низький, “відправити” відповідь через mock tool.
7. Якщо ризик високий або контекст недостатній, перейти в human review.
8. Після review відновити виконання і завершити workflow.

## Приклади вхідних запитів

- “I want a refund for the last payment.”
- “How do I delete my account?”
- “Why does your API return rate limit errors?”
- “Can you explain the difference between the Pro and Team plans?”
- “Please cancel my subscription immediately.”

## Очікувана поведінка

### Low-risk case

Користувач питає про тариф або технічне обмеження API. Агент знаходить відповідний документ, створює відповідь і автоматично її “надсилає”.

### High-risk case

Користувач просить повернення коштів, видалення акаунта або скасування підписки. Агент все одно готує чернетку, але перед фінальною дією ставить задачу на review і чекає підтвердження людини.

### Low-confidence case

Якщо retrieval повернув слабкі або суперечливі дані, агент не вигадує відповідь, а переводить кейс у human review.

## Чому цей проєкт добре підходить для підготовки до співбесіди

Це маленький проєкт, але він природно зачіпає майже всі ключові співбесідні теми:

- `LangChain vs LangGraph`
- agents vs deterministic workflows
- RAG architecture
- structured outputs
- tool calling
- state modeling
- branching and loops
- retries and failure handling
- human-in-the-loop
- checkpointing and persistence
- observability and tracing
- testing strategy

Головна перевага такого формату в тому, що ти не просто вчиш визначення, а можеш навести живий приклад власної реалізації.

## Основний сценарій користувача

1. Support ticket приходить у систему.
2. Workflow класифікує тип звернення.
3. Система запускає retrieval по внутрішній базі знань.
4. Модель формує draft reply лише на основі знайденого контексту.
5. Окремий крок оцінює ризик:
   - якщо відповідь безпечна, автоматичне відправлення;
   - якщо дія чутлива або невпевненість висока, human review.
6. Після human approval workflow resume-иться і виконує фінальний крок.

## Які можливості має реалізувати MVP

MVP не повинен бути перевантаженим. Достатньо реалізувати:

- один вхідний канал, наприклад CLI або простий web form;
- knowledge base з 10-20 markdown-документів;
- простий embeddings + vector store pipeline;
- 3-5 категорій support requests;
- генерацію чернетки відповіді;
- risk scoring;
- гілку auto-send vs human-review;
- mock tool для “відправлення” відповіді;
- persistence для state;
- кілька тестових сценаріїв.

## Функціональні вимоги

### 1. Ticket ingestion

Система повинна вміти приймати текст звернення, генерувати `ticket_id` і запускати workflow.

### 2. Ticket classification

Модель повинна класифікувати звернення у фіксовані категорії, наприклад:

- `billing`
- `refund`
- `account`
- `technical`
- `pricing`
- `other`

Краще повертати результат у вигляді structured output, а не парсити вільний текст.

### 3. Retrieval

На основі категорії та тексту звернення система повинна знайти релевантні документи у knowledge base.

### 4. Draft response generation

Відповідь повинна будуватися з опорою на retrieved context. Якщо релевантного контексту немає, система не повинна вигадувати впевнені відповіді.

### 5. Risk assessment

Окремий крок має вирішувати, чи:

- можна відповісти автоматично;
- потрібна ескалація людині;
- потрібно попросити більше інформації.

### 6. Human review

Для чутливих категорій workflow повинен вміти поставити виконання на паузу і чекати підтвердження або редагування відповіді людиною.

### 7. Final action

Після approval агент має виконати контрольований side effect через tool, наприклад записати результат у файл, лог або mock outbox.

## Нефункціональні вимоги

- Поведінка має бути відтворюваною і зручною для дебагу.
- State має бути прозорим і добре типізованим.
- Workflow не повинен зациклюватися без обмежень.
- Side effects мають бути ідемпотентними.
- Система має логувати ключові кроки.
- Бажано мати трасування викликів моделі, tools і retrieval.

## Архітектура високого рівня

Проєкт складається з двох шарів:

### Шар `LangChain`

Відповідає за LLM-компоненти:

- chat model;
- prompt templates;
- structured output schemas;
- embeddings;
- vector store;
- retriever;
- tool definitions.

### Шар `LangGraph`

Відповідає за orchestration:

- state schema;
- nodes;
- edges;
- branching;
- retries;
- interrupts;
- resume;
- checkpointing.

## Пропонований workflow у LangGraph

Можна побудувати такий граф:

1. `ingest_ticket`
2. `classify_ticket`
3. `retrieve_context`
4. `draft_response`
5. `assess_risk`
6. `human_review` або `send_response`
7. `close_ticket`

### Деталі вузлів

#### `ingest_ticket`

Ініціалізує state, додає `ticket_id`, вхідне повідомлення, статуси за замовчуванням.

#### `classify_ticket`

Використовує LLM зі structured output, щоб повернути категорію, коротке пояснення і, за бажанням, confidence score.

#### `retrieve_context`

Викликає retriever і додає в state релевантні документи або фрагменти.

#### `draft_response`

Генерує відповідь з опорою на retrieved context. Добре також зберігати citations або список джерел, щоб потім легше пояснювати, на основі чого створено відповідь.

#### `assess_risk`

Правило або окрема модельна нода, яка визначає:

- `low_risk_auto_send`
- `needs_human_review`
- `insufficient_context`

#### `human_review`

Pause point. Тут workflow зупиняється через interrupt і чекає рішення людини:

- approve;
- edit draft;
- reject and escalate;
- request more info.

#### `send_response`

Контрольований tool call, який емулює відправлення відповіді.

#### `close_ticket`

Фіналізує workflow, оновлює статус і зберігає результат.

## Приклад маршрутизації

- Якщо `category == pricing` і confidence висока, можна одразу відправляти.
- Якщо `category in [refund, account, billing]`, майже завжди потрібен review.
- Якщо `retrieved_docs` порожні або signal слабкий, направляємо в review.
- Якщо send tool падає, робимо retry до певної межі.

## Модель state

Приблизний приклад:

```python
from typing import Literal
from typing_extensions import TypedDict


class TicketState(TypedDict):
    ticket_id: str
    customer_message: str
    category: str
    classification_reason: str
    confidence: float
    retrieved_docs: list[str]
    draft_response: str
    risk_level: Literal["low", "medium", "high"]
    routing_decision: Literal["auto_send", "review", "need_more_info"]
    approval_status: Literal["pending", "approved", "rejected"]
    send_status: Literal["not_sent", "sent", "failed"]
    retry_count: int
    error_message: str
```

## Чому state важливо проєктувати акуратно

На співбесідах це часто окремий акцент. Хороший state:

- містить сирі дані, а не лише готовий текст;
- не змішує несумісні відповідальності;
- дозволяє перевикористовувати результати між нодами;
- полегшує дебаг і тестування;
- спрощує persistence і resume.

Поганий state зазвичай швидко перетворює workflow на непрозорий “ланцюжок prompt-ів”.

## Tools, які варто реалізувати

Навіть якщо частину логіки можна зробити просто функціями, корисно оформити ключові дії як tools, щоб попрактикувати контракти й безпечні side effects.

### `search_kb`

Приймає запит або категорію та повертає релевантні документи.

### `draft_reply`

Опціонально може бути або tool, або звичайний LLM step. Якщо це tool, він дозволяє відокремити етап формування чернетки.

### `send_reply`

Емулює відправлення відповіді. Для MVP краще не інтегрувати реальний email, а писати в outbox-файл або локальний лог.

### `escalate_to_human`

Створює позначку для review або генерує interrupt payload.

## Як реалізувати RAG

### Knowledge base

Створи невелику базу знань із 10-20 markdown-файлів, наприклад:

- `refund_policy.md`
- `billing_faq.md`
- `pricing_plans.md`
- `api_rate_limits.md`
- `account_deletion.md`
- `subscription_cancellation.md`
- `support_sla.md`

### Кроки RAG pipeline

1. Завантаження документів.
2. Нарізка на chunks.
3. Генерація embeddings.
4. Індексація у vector store.
5. Retrieval по запиту.
6. Передача контексту в ноду `draft_response`.

### На що звернути увагу

- chunk size і overlap;
- metadata для документів;
- фільтрація за категоріями;
- retrieval quality;
- обмеження кількості контексту;
- зниження hallucinations через grounded prompting.

## Human-in-the-loop

Це одна з найсильніших частин проєкту для співбесіди.

Workflow має вміти:

- зупинитися перед ризикованою дією;
- зберегти state;
- дочекатися зовнішнього рішення;
- продовжити виконання з того самого місця.

Приклади випадків для review:

- refund request;
- account deletion;
- cancellation with special conditions;
- суперечливий або неповний контекст;
- низька впевненість класифікації;
- невдала відповідь після кількох retries.

## Error handling і retries

Проєкт варто відразу будувати так, ніби він піде в production.

Продумай кілька типів помилок:

- тимчасове падіння LLM API;
- падіння vector store або retriever;
- відсутність документів;
- невалідний structured output;
- збій send tool.

Рекомендована стратегія:

- транзієнтні помилки: retry;
- LLM parsing issues: перегенерація або fallback;
- відсутність контексту: review або request more info;
- фатальні помилки: завершення зі статусом `failed` і записом в лог.

Обов’язково додай:

- `retry_count`;
- максимальний ліміт повторів;
- idempotent send logic;
- зрозуміле логування.

## Idempotency

Навіть у навчальному проєкті це корисно показати.

Якщо `send_response` буде викликано повторно через retry або resume, система не повинна “надсилати” ту саму відповідь двічі. Це можна реалізувати через:

- перевірку `send_status`;
- збереження `ticket_id` у mock outbox;
- дедуплікацію по request key.

## Observability і tracing

Якщо є можливість, додай трасування викликів:

- класифікація;
- retrieval;
- генерація відповіді;
- tool calls;
- branching decisions;
- retries;
- human approvals.

Для цього добре підходить `LangSmith`, але для MVP можна почати хоча б із структурованих локальних логів.

## Testing strategy

Проєкт дуже зручно тестувати по шарах.

### Unit tests

Окремо тестуй:

- classification node;
- routing logic;
- risk rules;
- send tool;
- reducers або state transforms.

### Integration tests

Перевіряй повний workflow на сценаріях:

- pricing question -> auto-send;
- refund question -> human review;
- unknown request -> review;
- missing docs -> request more info;
- send tool failure -> retry -> success.

### Evaluation cases

Добре мати маленький набір ticket examples, щоб перевіряти регресії після змін prompts або routing logic.

## Що можна показати в демо

Найкраще працює серія коротких прикладів:

1. Просте технічне питання, яке проходить повний auto-send path.
2. Refund ticket, який доходить до human review.
3. Слабкий retrieval case, де система не вигадує відповідь.
4. Симульований send failure з retry.
5. Resume після approval.

## Пропонована структура папок

```text
project/
  README.md
  requirements.txt
  .env.example
  app/
    main.py
    graph.py
    state.py
    nodes/
      ingest.py
      classify.py
      retrieve.py
      draft.py
      risk.py
      review.py
      send.py
    tools/
      search_kb.py
      send_reply.py
    rag/
      loader.py
      index.py
      retriever.py
    schemas/
      classification.py
      review.py
    storage/
      checkpoints.py
      outbox.py
    prompts/
      classify.txt
      draft_response.txt
      risk_check.txt
  knowledge_base/
    refund_policy.md
    billing_faq.md
    pricing_plans.md
    api_rate_limits.md
    account_deletion.md
  tests/
    test_classification.py
    test_routing.py
    test_send_tool.py
    test_workflow.py
```

## Рекомендований стек

- `Python`
- `langchain`
- `langgraph`
- embeddings provider на твій вибір
- простий vector store, наприклад `FAISS` або `Chroma`
- `pydantic` для structured schemas
- `pytest` для тестів

## Поетапний план реалізації

### Етап 1. Базовий RAG без графа

Побудуй простий pipeline:

- завантаження knowledge base;
- embeddings;
- vector store;
- retriever;
- генерація відповіді на основі retrieved docs.

Це дасть базу для розуміння `LangChain`.

### Етап 2. Structured classification

Додай LLM-класифікацію звернень через schema-based output. На цьому етапі вже можна почати пояснювати structured outputs на співбесіді.

### Етап 3. Перенесення в LangGraph

Розбий процес на nodes і edges. Додай `StateGraph`, state schema і routing decisions.

### Етап 4. Risk-based branching

Реалізуй гілку `auto_send` vs `review`.

### Етап 5. Human review

Додай interrupt/resume і persistence.

### Етап 6. Reliability

Додай retries, idempotency, logging, тестові сценарії.

## Які співбесідні питання цей проєкт покриває

### Про `LangChain`

- Що таке agent?
- Як працюють tools?
- Як робити structured output?
- Як побудувати RAG?
- Як зменшити hallucinations?

### Про `LangGraph`

- Що таке `State`, `Node`, `Edge`?
- Чому graph кращий за простий loop?
- Як працює branching?
- Як реалізується human-in-the-loop?
- Навіщо потрібні checkpointing і durable execution?

### Про production design

- Як контролювати side effects?
- Як уникати нескінченних циклів?
- Як тестувати workflow?
- Як робити retry safely?
- Як організувати observability?

## Як красиво презентувати цей проєкт на співбесіді

Хороший короткий опис може звучати так:

> Я зробив невеликий support inbox agent. Просту LLM-частину я зібрав через LangChain: structured classification, retrieval і draft generation. Оркестрацію побудував у LangGraph, бо мені були потрібні state, branching, human approval і resume. Для low-risk запитів система відповідає автоматично, а для refund/account-related кейсів workflow зупиняється на review. Додав retries, checkpointing і базові тести, щоб система була ближча до production-поведінки.

## Можливі розширення після MVP

Коли базова версія запрацює, можна додати:

- confidence scoring;
- multi-step retrieval;
- citation-aware responses;
- окрему risk policy engine;
- UI для review;
- справжню email або ticket інтеграцію;
- аналітику по категоріях і якості відповідей;
- evaluation dataset для автоматичної перевірки якості.

## Що не варто ускладнювати на старті

Щоб не втратити темп, не потрібно одразу:

- підключати реальний email provider;
- будувати складний frontend;
- робити multi-agent систему;
- додавати багато зовнішніх інтеграцій;
- оптимізувати все під високе навантаження.

Для навчання важливіше мати чітку, завершену архітектуру, ніж надмірно великий scope.

## Критерії готовності

Можна вважати MVP завершеним, якщо:

- є knowledge base і retrieval;
- є structured classification;
- є `LangGraph` workflow;
- працює branching;
- є human review path;
- є mock send tool;
- є хоча б 4-5 тестових сценаріїв;
- ти можеш пояснити, чому певні кроки зробив через `LangChain`, а orchestration через `LangGraph`.

## Підсумок

`AI Support Inbox Agent` — це невеликий, але дуже сильний навчальний проєкт для підготовки до співбесіди. Він дає не лише практику з `LangChain` і `LangGraph`, а й правильне інженерне мислення: як проєктувати workflow, як тримати state, як робити безпечні дії, як обробляти помилки і як перетворювати LLM-логіку на підтримувану систему.

Якщо твоя ціль — не просто “запустити агента”, а навчитися пояснювати архітектурні рішення на співбесіді, цей формат майже ідеальний.
