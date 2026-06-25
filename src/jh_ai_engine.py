# jh_ai_engine.py
import json
import re
import urllib.request
import urllib.error
import time

def clean_and_parse_json(raw_text):
    """
    Интеллектуально очищает строку от мусора ИИ (Markdown разметки, лишнего текста)
    и безопасно преобразует её в валидный Python-словарь.
    """
    if not raw_text:
        raise ValueError("Получен пустой ответ от ИИ.")

    clean_text = raw_text.strip()
    
    # Исправленный чистый регулярный парсер markdown-тегов ```json
    if clean_text.startswith("```"):
        clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
    clean_text = clean_text.strip()
    
    # Находим границы JSON объекта по первой открывающейся и последней закрывающейся скобке
    match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
    if not match:
        raise ValueError("ИИ не вернул JSON-структуру (отсутствуют фигурные скобки).")
    
    json_str = match.group(1)
    
    # Исправляем классическую ошибку LLM — висящие запятые перед закрывающими скобками: ,} или ,]
    json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[ИИ-Движок-Ошибка]: Ошибка декодирования JSON. Сырой текст: {json_str}")
        raise ValueError(f"ИИ вернул поврежденный формат данных: {str(e)}")


class BaseProvider:
    """Базовый абстрактный класс провайдера ИИ с каскадным переключением (Failover Chain)."""
    def __init__(self, api_key, model_pool):
        self.api_key = api_key
        self.model_pool = model_pool  # Список приоритетных моделей

    def make_request(self, model_name, contents, system_instruction):
        """Реализуется в дочерних классах провайдеров."""
        raise NotImplementedError

    def call_with_failover(self, contents, system_instruction):
        """
        Логика Failover Chain: выполняет последовательный обход пула моделей провайдера.
        Если запрос падает из-за лимитов, таймаута или ошибки 5xx, переходит к следующей модели.
        """
        if not self.api_key:
            raise ValueError("Ключ API отсутствует для выбранного провайдера.")
        if not self.model_pool:
            raise ValueError("Список активных моделей пуст.")

        last_exception = None
        for model_name in self.model_pool:
            print(f"[ИИ-Движок]: Запуск запроса на модели {model_name}...")
            for attempt in range(3):
                try:
                    return self.make_request(model_name, contents, system_instruction)
                except urllib.error.HTTPError as e:
                    status = e.code
                    last_exception = e
                    
                    # Если исчерпан лимит частоты (429) или сбой сервера (502, 503, 504)
                    if status in [429, 502, 503, 504]:
                        time.sleep(2 ** attempt)  # Экспоненциальный откат
                        continue
                        
                    # Если ошибка авторизации (401, 403), нет смысла пробовать другие модели
                    if status in [401, 403]:
                        raise ValueError(f"Ошибка авторизации API: {status}. Проверьте правильность ключа.")
                    
                    print(f"[ИИ-Движок]: Модель {model_name} вернула ошибку {status}. Пробуем следующую модель в каскаде...")
                    break
                except Exception as e:
                    print(f"[ИИ-Движок]: Сетевой сбой модели {model_name}: {str(e)}")
                    last_exception = e
                    time.sleep(1)
                    break
                    
        raise RuntimeError(f"Все модели в пуле провайдера завершились сбоем. Последняя ошибка: {str(last_exception)}")


class GeminiProvider(BaseProvider):
    """Провайдер Google Gemini API (поддержка 3-го поколения моделей)."""
    def make_request(self, model_name, contents, system_instruction):
        # ФИКС: Убран Markdown-синтаксис, ссылка теперь абсолютно чистая и валидная
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": contents}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "generationConfig": {"temperature": 0.1}
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            
            # Защита от блокировок безопасности и пустого вывода
            candidates = res_data.get('candidates', [])
            if not candidates:
                block_reason = res_data.get('promptFeedback', {}).get('blockReason', 'Блокировка безопасности или пустой ответ')
                raise ValueError(f"Gemini API не вернул варианты ответа. Причина: {block_reason}")
                
            content = candidates[0].get('content', {})
            parts = content.get('parts', [])
            if not parts:
                raise ValueError("Ответ Gemini пуст или заблокирован фильтром контента.")
                
            return parts[0].get('text', '').strip()


class OpenAIProvider(BaseProvider):
    """Провайдер OpenAI API (совместимый с gpt-5 и o3 моделями)."""
    def make_request(self, model_name, contents, system_instruction):
        # ФИКС: Убран Markdown-синтаксис
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": contents}
            ],
            "temperature": 0.1
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            choices = res_data.get('choices', [])
            if not choices:
                raise ValueError("OpenAI API вернул пустой список вариантов.")
            return choices[0]['message']['content'].strip()


class AnthropicProvider(BaseProvider):
    """Провайдер Anthropic Claude API (поддержка claude-4-семейства)."""
    def make_request(self, model_name, contents, system_instruction):
        # ФИКС: Убран Markdown-синтаксис
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "content-type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        payload = {
            "model": model_name,
            "system": system_instruction,
            "messages": [
                {"role": "user", "content": contents}
            ],
            "max_tokens": 2048,
            "temperature": 0.1
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            content = res_data.get('content', [])
            if not content:
                raise ValueError("Anthropic API вернул пустой контент ответа.")
            return content[0].get('text', '').strip()


class DeepSeekProvider(BaseProvider):
    """Провайдер DeepSeek API."""
    def make_request(self, model_name, contents, system_instruction):
        # ФИКС: Убран Markdown-синтаксис
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": contents}
            ],
            "temperature": 0.1
        }
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            choices = res_data.get('choices', [])
            if not choices:
                raise ValueError("DeepSeek API вернул пустой список вариантов.")
            return choices[0]['message']['content'].strip()


def get_provider(provider_name, api_key, model_pool):
    """Фабричный метод инициализации нужного провайдера."""
    providers = {
        "Gemini": GeminiProvider,
        "OpenAI": OpenAIProvider,
        "Anthropic": AnthropicProvider,
        "DeepSeek": DeepSeekProvider
    }
    provider_cls = providers.get(provider_name)
    if not provider_cls:
        raise ValueError(f"Неизвестный провайдер: {provider_name}")
    return provider_cls(api_key, model_pool)


def analyze_and_generate(vacancy, config):
    """
    Вызывает двухстадийный анализ вакансии через выбранного провайдера ИИ.
    stage1: фильтрация и извлечение структурированной информации в JSON.
    stage2: автогенерация качественного сопроводительного письма.
    """
    provider_name = config.get("current_provider", "Gemini")
    api_keys = config.get("api_keys", {})
    api_key = api_keys.get(provider_name, "").strip()
    
    active_models = config.get("active_models", {})
    model_pool = active_models.get(provider_name, [])

    if not api_key:
        return "ERROR", f"Отсутствует API ключ для провайдера {provider_name}.", {}
    if not model_pool:
        return "ERROR", f"Не выбрана ни одна рабочая модель для провайдера {provider_name}.", {}

    raw_title = vacancy.get('title', 'Не указано')
    raw_text = vacancy.get('text', '')
    first_name = config.get("first_name", "Соискатель")
    resume_text = config.get("resume", "")

    # Описание правил первичной фильтрации на Stage 1
    stage1_system_instruction = (
        "You are an expert career tracker and highly practical job filter agent. Your main goal is to maintain a strict balance: "
        "filter out roughly 50-60% of low-quality, exploitative, scam, or overly demanding vacancies (REDFLAG / reject), "
        "and approve only the best 40-50% of genuine, balanced, professional opportunities that match the candidate's professional profile.\n\n"
        "Analyze the job description carefully based on the candidate's resume/skills profile and evaluate the following quality criteria:\n"
        "1. PROFESSION MATCH & ADEQUACY (Strict check):\n"
        "   - The job must be a professional role matching the candidate's background/resume (if provided). "
        "     If the candidate's resume is empty, evaluate the job as a general IT, marketing, sales, administrative, support, creative, or digital role. "
        "     REJECT immediately (set 'is_relevant_profession' to false) if it is manual/unskilled labor: drivers, couriers, cleaners, loaders, etc.\n"
        "2. CRITICAL SCAMS & GREY SCHEMES (MANDATORY REJECTION):\n"
        "   - Network marketing (MLM, referral networks) and financial pyramids.\n"
        "   - Esoterics, astrology, numerology, tarot reading, magic.\n"
        "   - Hidden upfront costs (demands to buy starting packs, pay for courses, software, or security deposits).\n"
        "   - Grey crypto schemes, P2P arbitrage, gambling/betting promotion, money laundering, bank card setups.\n"
        "3. EXPLOITATION & WORKLOAD FILTERS (Reject if any of these apply):\n"
        "   - Overworked Schedule: Calculate total weekly working hours. If the weekly load strictly exceeds 40-45 hours, mark as REDFLAG (reject).\n"
        "   - Exploitative schedule: Ready to work 24/7, constant unpaid overtime, night shifts without extra compensation.\n"
        "   - Aggressive / Infobusiness marketing slang: Words like 'сильные воронки', 'групповые собеседования', 'массовый набор', 'поток откликов'.\n"
        "   - Unreasonable ratio of salary to duties.\n"
        "   - Lack of concreteness: Only contains water about 'success', but lists zero actual duties.\n\n"
        "Your verdict must be moderately strict. Ignore standard corporate clichés if duties are clear.\n"
        "You MUST respond ONLY with a valid raw JSON object. Do not include markdown code blocks, do not include explanations, just raw JSON.\n"
        "The JSON object must contain exactly these keys:\n"
        "{\n"
        "  \"is_relevant_profession\": boolean,\n"
        "  \"reject_reason\": string (in Russian if false, empty if true),\n"
        "  \"extracted_title\": string (Russian title),\n"
        "  \"extracted_company\": string (Russian clean company),\n"
        "  \"work_format\": \"remote\" | \"office\" | \"hybrid\" | \"unknown\",\n"
        "  \"requires_local_presence\": boolean\n"
        "}"
    )
    
    stage1_prompt = f"Candidate Profile (Resume):\n{resume_text}\n\nJob Title: {raw_title}\n\nPage Text:\n{raw_text[:8000]}"

    try:
        provider = get_provider(provider_name, api_key, model_pool)
        res_text = provider.call_with_failover(stage1_prompt, stage1_system_instruction)
        
        # Задействуем интеллектуальный безопасный парсер JSON
        result_json = clean_and_parse_json(res_text)
        
        # Гарантируем наличие всех ключей
        extracted_title = result_json.get("extracted_title", raw_title)
        extracted_company = result_json.get("extracted_company", "Не указана")
        extracted_data = {"title": extracted_title, "company": extracted_company}

        # Если вакансия заблокирована ИИ по критериям адекватности
        if not result_json.get("is_relevant_profession", True):
            return "REJECTED", result_json.get("reject_reason", "Не прошло фильтр качества вакансий"), extracted_data

        work_format = result_json.get("work_format", "unknown")
        f_remote = config.get("filter_remote")
        f_office = config.get("filter_office")
        f_hybrid = config.get("filter_hybrid")

        # Применяем фильтр формата работы на основе чекбоксов в UI
        if f_remote or f_office or f_hybrid:
            if work_format == "remote" and not f_remote:
                return "REJECTED", "Удаленная работа отключена в настройках приложения.", extracted_data
            elif work_format == "office" and not f_office:
                return "REJECTED", "Работа в офисе отключена в настройках приложения.", extracted_data
            elif work_format == "hybrid" and not f_hybrid:
                return "REJECTED", "Гибридная работа отключена в настройках приложения.", extracted_data

        # Применяем проверку локации (физ. присутствие в РФ / VPN)
        if config.get("filter_no_rf") and result_json.get("requires_local_presence", False):
            return "REJECTED", "Требуется физическое присутствие на территории РФ или запрещен VPN.", extracted_data

    except Exception as e:
        return "ERROR", f"Сбой каскада ИИ на Stage 1: {str(e)}", {}

    # Запускаем Stage 2: генерация сопроводительного письма
    stage2_system_instruction = (
        f"You are an HR expert. Write a professional cover letter on behalf of {first_name} in 2-3 short paragraphs. "
        f"The letter MUST be written entirely in Russian language. No fluff. At the very end of the letter, "
        f"MANDATORILY add the closing signature: 'С уважением, {first_name}'."
    )
    stage2_prompt = f"Resume:\n{resume_text}\n\nVacancy: {extracted_title} in company {extracted_company}\nDescription:\n{raw_text[:4000]}"

    try:
        letter_text = provider.call_with_failover(stage2_prompt, stage2_system_instruction)
        return "APPROVED", letter_text, extracted_data
    except Exception as e:
        return "ERROR", f"Сбой каскада ИИ на Stage 2: {str(e)}", extracted_data