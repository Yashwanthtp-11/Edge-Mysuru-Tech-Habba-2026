"""Provider-agnostic grounded prompt builder for the RAG layer.

This module deliberately only constructs a prompt string. It does not call any external
LLM provider or install any SDK.
"""


def build_grounded_prompt(predicted_label, confidence, retrieved_document, source):
    """Return a strict prompt that grounds the LLM on retrieved agricultural evidence only."""
    if not predicted_label:
        raise ValueError("predicted_label is required")
    if confidence is None:
        raise ValueError("confidence is required")
    if not retrieved_document:
        raise ValueError("retrieved_document is required")

    prompt = f"""You are a farm advisory assistant.

Possible diagnosis from the vision model:
- Label: {predicted_label}
- Confidence: {confidence:.6f}

Important constraints:
- This is a possible diagnosis, not a confirmed diagnosis.
- Use ONLY the retrieved agricultural evidence provided below.
- Do not invent symptoms, management advice, or disease facts.
- Do not invent pesticide names, dosages, concentrations, or application schedules.
- Do not override the vision prediction; instead present it as a model assessment.
- If the evidence is insufficient, say so clearly.

Retrieved agricultural evidence:
{retrieved_document}

Source:
{source}

Please answer in this structure:
1. What the image suggests
2. Symptoms
3. Recommended management
4. Prevention
5. Important caution
6. Source

Keep the response concise, farmer-friendly, and grounded only in the supplied evidence.
"""
    return prompt


def build_answer(prediction, retrieved_documents):
    """Backward-compatible helper that converts the supplied inputs into a grounded prompt."""
    predicted_label = prediction.get("predicted_label")
    confidence = prediction.get("confidence")
    retrieved_document = retrieved_documents.get("content") if isinstance(retrieved_documents, dict) else retrieved_documents
    source = retrieved_documents.get("path") if isinstance(retrieved_documents, dict) else "Unknown source"
    return build_grounded_prompt(predicted_label, confidence, retrieved_document, source)
