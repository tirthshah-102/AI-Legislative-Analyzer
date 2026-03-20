from .compressor import ScaleDownClient
from deep_translator import GoogleTranslator

class LegislativeAnalyzer:
    def __init__(self):
        self.client = ScaleDownClient()
        self.lang_map = {
            "Hindi": "hi",
            "Gujarati": "gu",
            "English": "en"
        }

    def _translate_if_needed(self, text, target_language):
        """Helper to translate text if not English."""
        if target_language == "English" or not text:
            return text
        
        target_code = self.lang_map.get(target_language, "en")
        try:
            # Note: GoogleTranslator has a character limit (~5000), 
            # so we might need to chunk if the text is very long.
            translator = GoogleTranslator(source='auto', target=target_code)
            if len(text) > 4500:
                # Simple chunking logic
                chunks = [text[i:i + 4500] for i in range(0, len(text), 4500)]
                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                return "".join(translated_chunks)
            return translator.translate(text)
        except Exception as e:
            return f"{text}\n\n(Translation Error: {e})"

    def generate_summary(self, text, language="English"):
        """
        Generates a highly detailed, full-length, point-wise structured summary in very simple language.
        Generates directly in the requested language.
        """
        prompt = f"""
        You are a PRO LEGISLATIVE ADVISOR with 20 years of experience in simplifying complex laws for citizens.
        TASK: Analyze the provided legislative document and create a HIGHLY DETAILED, FULL-LENGTH, POINT-WISE summary.

        ⚠️ LANGUAGE AND CLARITY RULES:
        - The absolute MOST IMPORTANT RULE is to generate your entire response in **{language}**.
        - Use very simple language that a 10-year-old could understand. NO LEGALESE.
        - Be precise and objective.
        - Ensure every point is actionable or informative for a regular citizen.

        ⚠️ STYLING & FORMATTING RULES:
        - Use ## for Section Headings.
        - Use **bold** for key legal terms, dates, and amounts.
        - Use bullet points (- ) for all details.
        - The summary must be detailed and cover all important aspects of the document.
        - NO paragraphs. NO introductory or concluding prose.

        ## 🎯 Purpose & Main Objectives
        - State clearly what this document/act intends to solve.
        - Highlight the primary goal.

        ## 📜 Key Provisions & Rules
        - Breakdown the major sections into easy-to-understand rules.
        - Include specific **limits**, **percentages**, or **criteria**.

        ## 👥 Impact on the Public
        - Clearly list **benefits**, **rights**, and **obligations** for the citizen.
        - Use "You can..." or "Citizens must..." for direct impact.

        ## ⚠️ Compliance & Penalties
        - List exact **fines**, **punishments**, or **deadlines**.
        - Be specific about what constitutes a violation.

        ## 📅 Critical Dates & Timelines
        - List enforcement dates and expiry periods.

        IF DATA IS MISSING: Write "- **Information Note**: Not specified in this document."
        """
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        if error:
            print(f"DEBUG: Summary Error: {error}")
            return f"Error generating summary: {error}", {"original_tokens": 0, "compressed_tokens": 0, "ratio": 1.0}
        print(f"DEBUG: Raw Summary Result keys: {result.keys() if isinstance(result, dict) else type(result)}")
        results = result.get("results", {})
        final_output = results.get("compressed_prompt", "")
        
        if not final_output:
            print(f"DEBUG: {language} output is empty!")

        metrics = {
            "original_tokens": result.get("total_original_tokens", 0),
            "compressed_tokens": result.get("total_compressed_tokens", 0),
            "ratio": result.get("request_metadata", {}).get("average_compression_ratio", 1.0)
        }
        
        # We instruct the LLM to output directly in the target language.
        # However, because ScaleDown compresses everything back into English (mostly), 
        # we still must run the translation step.
        translated_output = self._translate_if_needed(final_output, language)
        return translated_output, metrics

    def generate_compliance_checklist(self, text, language="English"):
        """
        Extracts penalties and obligations and turns them into a checklist.
        """
        prompt = """
        TASK: Extract all compliance-related obligations and penalties from this document.
        FORMAT: Generate a 'To-Do' checklist for a citizen to remain compliant.
        
        RULES:
        - Use "[]" (empty brackets) to start each line.
        - Each item must be a short, actionable task (e.g., "[] Register with the local authority by Dec 31").
        - Categorize into 'Immediate Actions' and 'Ongoing Obligations'.
        - Use ## for headers.
        """
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        if error: return f"Error: {error}"
        return self._translate_if_needed(result.get("results", {}).get("compressed_prompt", ""), language)

    def extract_citations_and_entities(self, text, language="English"):
        """
        Identifies references to other acts and provides context.
        """
        prompt = """
        TASK: Find all mentions of OTHER laws/acts (e.g., "Section 12 of Act X").
        For each mention, provide:
        - **Citation**: The exact text found.
        - **Context**: A 1-sentence explanation of what that referenced law generally covers.
        
        Format as a bulleted list.
        """
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        if error: return f"Error: {error}"
        return self._translate_if_needed(result.get("results", {}).get("compressed_prompt", ""), language)

    def analyze_risk_and_complexity(self, text, language="English"):
        """
        Scores the document on various metrics for visualization.
        Because the ScaleDown API strips JSON formatting, we use a heuristic approach
        based on the compressed text content to generate realistic scores.
        """
        prompt = "Summarize the key compliance rules, penalties, and citizen rights in this document."
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        raw_text = result.get("results", {}).get("compressed_prompt", "") if not error else text
        raw_text_lower = raw_text.lower()
        
        # Heuristics based on keyword density in the compressed summary
        complexity = min(100, 30 + (len(raw_text) // 100) + (raw_text_lower.count("section") * 2) + (raw_text_lower.count("article") * 2))
        burden = min(100, 20 + (raw_text_lower.count("must") * 5) + (raw_text_lower.count("required") * 5) + (raw_text_lower.count("shall") * 3))
        risk = min(100, 10 + (raw_text_lower.count("penalty") * 10) + (raw_text_lower.count("fine") * 10) + (raw_text_lower.count("punishment") * 10) + (raw_text_lower.count("violation") * 5))
        protection = min(100, 40 + (raw_text_lower.count("right") * 5) + (raw_text_lower.count("benefit") * 5) + (raw_text_lower.count("entitled") * 5) + (raw_text_lower.count("rebate") * 10))
        
        return {"complexity": int(complexity), "burden": int(burden), "risk": int(risk), "protection": int(protection)}

    def extract_timeline_data(self, text, language="English"):
        """
        Extracts dates and events for a visual timeline.
        Uses heuristics since ScaleDown API removes JSON array formatting.
        """
        prompt = "List all important dates, deadlines, and milestones mentioned in this document."
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        timeline = []
        if error: return timeline
        
        raw_text = result.get("results", {}).get("compressed_prompt", "")
        # Simple extraction: look for years like 2024, 2025, 2026, 2030 in the text
        import re
        sentences = raw_text.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            # Look for years (4 digits starting with 20)
            year_match = re.search(r'\b(20\d{2})\b', sentence)
            if year_match and len(sentence) > 10:
                timeline.append({
                    "date": year_match.group(1),
                    "event": self._translate_if_needed(sentence[:100] + "...", language)
                })
        
        # If no strict years found, provide a generic timeline based on standard acts
        if not timeline:
             timeline = [
                 {"date": "Day 1", "event": self._translate_if_needed("Act comes into effect", language)},
                 {"date": "Year 1", "event": self._translate_if_needed("Initial compliance deadline", language)}
             ]
             
        # Deduplicate by date
        unique_timeline = []
        seen_dates = set()
        for item in timeline:
            if item["date"] not in seen_dates:
                seen_dates.add(item["date"])
                unique_timeline.append(item)
                
        return list(unique_timeline)[:5] # Limit to top 5

    def extract_entity_map(self, text, language="English"):
        """
        Identifies connections between entities.
        Uses heuristics since ScaleDown API removes JSON array formatting.
        """
        prompt = "List the main government bodies, organizations, or groups (like 'Citizens' or 'Businesses') mentioned in this document."
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        entities = []
        if error: return entities
        
        raw_text = result.get("results", {}).get("compressed_prompt", "")
        raw_text_lower = raw_text.lower()
        
        # Standard entities to look for
        standard_entities = ["government", "citizens", "businesses", "committee", "authority", "court", "council", "industry", "farmers"]
        found_entities = []
        
        for entity in standard_entities:
            if entity in raw_text_lower:
                found_entities.append(entity.capitalize())
        
        # Build relationships
        if "Government" in found_entities and "Citizens" in found_entities:
            entities.append({"source": self._translate_if_needed("Government", language), "target": self._translate_if_needed("Citizens", language), "relationship": self._translate_if_needed("Regulates/Provides Benefits to", language)})
        if "Government" in found_entities and "Businesses" in found_entities:
            entities.append({"source": self._translate_if_needed("Government", language), "target": self._translate_if_needed("Businesses", language), "relationship": self._translate_if_needed("Enforces rules on", language)})
        if "Authority" in found_entities:
            entities.append({"source": self._translate_if_needed("Authority", language), "target": self._translate_if_needed("Document Scope", language), "relationship": self._translate_if_needed("Oversees implementation", language)})
            
        # Fallback if none found
        if not entities:
             entities.append({"source": self._translate_if_needed("State", language), "target": self._translate_if_needed("Public", language), "relationship": self._translate_if_needed("Governs", language)})
             
        return entities

    def compare_bills_analysis(self, text1, text2, language="English"):
        """
        Compares two versions of a document and highlights differences.
        Uses Python difflib instead of ScaleDown API to maintain markdown formatting.
        """
        import difflib
        import re

        # Split texts into readable sentences
        sentences1 = [s.strip() for s in re.split(r'(?<=[.!?]) +|\n+', text1) if len(s.strip()) > 10]
        sentences2 = [s.strip() for s in re.split(r'(?<=[.!?]) +|\n+', text2) if len(s.strip()) > 10]

        differ = difflib.Differ()
        diff = list(differ.compare(sentences1, sentences2))

        added = []
        removed = []

        for line in diff:
            if line.startswith('+ '):
                added.append(line[2:])
            elif line.startswith('- '):
                removed.append(line[2:])

        # Build Markdown
        md = f"## {self._translate_if_needed('Document Comparison Analysis', language)}\n\n"
        
        md += f"### 🟢 {self._translate_if_needed('New Provisions Added (Version 2)', language)}\n"
        if added:
            for item in added[:10]: # limit to 10
                md += f"- **{self._translate_if_needed('Added', language)}**: {self._translate_if_needed(item, language)}\n"
            if len(added) > 10:
                md += f"- *...{self._translate_if_needed('and', language)} {len(added) - 10} {self._translate_if_needed('more additions', language)}.*\n"
        else:
            md += f"- {self._translate_if_needed('No major additions found.', language)}\n"

        md += f"\n### 🔴 {self._translate_if_needed('Provisions Removed (From Version 1)', language)}\n"
        if removed:
            for item in removed[:10]:
                md += f"- **{self._translate_if_needed('Removed', language)}**: {self._translate_if_needed(item, language)}\n"
            if len(removed) > 10:
                md += f"- *...{self._translate_if_needed('and', language)} {len(removed) - 10} {self._translate_if_needed('more removals', language)}.*\n"
        else:
            md += f"- {self._translate_if_needed('No major removals found.', language)}\n"

        return md

    def ask_question(self, text, question, language="English"):
        """
        Answers a specific question with senior-level legal expertise in point-wise format.
        """
        prompt = f"""
        You are an AI assistant that answers questions ONLY using the uploaded document.

        Instructions:
        1. Always read the uploaded document before answering.
        2. Find the relevant information inside the document that matches the user's question.
        3. Generate the answer based strictly on the document content.
        4. Do NOT answer using general knowledge or summaries.
        5. If the answer is not present in the document, respond with:
           "The answer is not available in the uploaded document."
        6. Provide clear and accurate answers based on the exact document information.
        7. If possible, quote or reference the relevant section from the document.
        8. The answer must be derived from the document content, not from a pre-generated summary.

        Goal:
        Ensure that every response is grounded in the uploaded document and directly answers the user's question using that document.

        QUESTION: {question}
        """
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        if error:
            print(f"DEBUG: Ask Error: {error}")
            return f"Error answering question: {error}", {}
            
        print(f"DEBUG: Raw Ask Result: {result}")
        results = result.get("results", {})
        english_output = results.get("compressed_prompt", "").strip()
        
        metrics = {
            "original_tokens": result.get("total_original_tokens", 0),
            "compressed_tokens": result.get("total_compressed_tokens", 0),
            "ratio": result.get("request_metadata", {}).get("average_compression_ratio", 1.0)
        }
        
        translated_output = self._translate_if_needed(english_output, language)
        return translated_output, metrics

    def extract_glossary(self, text, language="English"):
        """
        Extracts complex legal terms and provides high-accuracy simplified definitions.
        """
        prompt = "EXPERT ANALYSIS: Identify and define the top 5 most important legal/technical terms in this text. Provide a clear, accurate, one-sentence definition for each. Format as 'Term: Definition'."
        result, error = self.client.compress_context(text, prompt, model="gpt-4o")
        
        if error:
            print(f"DEBUG: Glossary Error: {error}")
            return f"Error extracting glossary: {error}"
            
        print(f"DEBUG: Raw Glossary Result: {result}")
        results = result.get("results", {})
        english_output = results.get("compressed_prompt", "")
        
        return self._translate_if_needed(english_output, language)
