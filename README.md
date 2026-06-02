# grc2prompt Policy Passport -- Technical Concept
Convert your GRC policies into AI-native guardrails / paste once, enforce everywhere.

Parts of the German-to-English translation and wording in this document were assisted by Claude (Anthropic).

**Version:** 0.1 (Proof of Concept)  
**Status:** Draft  
**License:** MIT
---

## Proof of Concept available online:
The current Policy Passport generator can be tested here: https://ozel0t-g.github.io/grc2prompt/

This is an early proof of concept intended for testing and discussion. Please do not use real company policies, personal data, confidential information, credentials, internal system details, or security-sensitive content when testing the online version. The current demo uses a free external AI service for generation, so any submitted text may be processed outside your organization’s controlled environment.

Use synthetic, anonymized, or example policy text only.

##

## Command Line Tool Technical Guide

The repository includes a Python based command line prototype for generating Policy Passport artifacts from plain policy text. It is designed as a portable reference implementation that can run on macOS, Linux, and Windows with Python 3 and the Python standard library. No package installation is required for the current version.

### 1. Purpose

The command line tool performs the same core work as the web proof of concept. It reads a policy document, builds the Policy Passport extraction prompt, sends the request to an OpenAI compatible text endpoint, extracts the JSON object from the model response, normalizes the result, and writes both a structured JSON artifact and a plain text Passport artifact.

The tool is useful when policy conversion should be repeatable, scriptable, or integrated into a local workflow. It can be used by a security team to convert test policies, by an engineer to validate generated Passport JSON, or by a governance team to prepare artifacts for review before wider deployment.

### 2. Requirements

Python 3 must be available on the machine.

On macOS and Linux, check the Python version with:

```bash
python3 --version
```

On Windows, check the Python version with:

```powershell
py --version
```

The generate command requires internet access because the current proof of concept sends the policy text to an external AI endpoint. The prompt and validate commands can be used without an external service.

### 3. Security Notice

The default generate command uses the same proof of concept endpoint as the browser version. Submitted policy text is sent to `https://text.pollinations.ai/openai` with the model value `openai-fast`.

Only use synthetic, public, or fully sanitized test data with this endpoint. Do not submit real company policies, personal data, customer data, secrets, credentials, internal system details, source code, legal material, incident details, or regulated information. For production use, replace the default endpoint with an approved enterprise model gateway or a provider that matches your security and compliance requirements.

The tool requires explicit confirmation before sending data to the external endpoint. This is done with the `--yes` option.

### 4. Generate a Passport

Create a text file that contains a sanitized policy example. Then run:

```bash
python3 grc2prompt.py generate policy.txt --yes --json-out passport.json --text-out passport.txt
```

On Windows, the same command can be run with the Python launcher:

```powershell
py grc2prompt.py generate policy.txt --yes --json-out passport.json --text-out passport.txt
```

The command creates two files. `passport.json` contains the normalized machine readable rule set. `passport.txt` contains the portable Policy Passport text block that can be pasted into an AI system prompt, project instruction field, or agent configuration.

### 5. Read Policy Text From Standard Input

The tool can also read policy text from standard input. This is useful for shell pipelines or simple automation.

```bash
cat policy.txt | python3 grc2prompt.py generate - --yes --text-out passport.txt
```

Windows PowerShell example:

```powershell
Get-Content policy.txt | py grc2prompt.py generate - --yes --text-out passport.txt
```

When the input path is omitted or set to `-`, the tool reads from standard input.

### 6. Create a Manual Prompt Without Calling an API

The prompt command builds the exact instruction package that would be sent to the model, but it does not call any external service. This is useful when a user wants to paste the prompt into ChatGPT, Claude, Gemini, Copilot, or an internal model interface.

```bash
python3 grc2prompt.py prompt policy.txt --output manualprompt.txt
```

The resulting prompt can be reviewed by a human before use. It also supports manual workflows where the JSON response is copied back into the tool for validation.

### 7. Validate or Convert an Existing Response

If a model response already exists, the validate command can parse it, extract the JSON object, fill missing defaults, and produce clean output files.

```bash
python3 grc2prompt.py validate rawresponse.json --json-out passport.json --text-out passport.txt
```

The parser accepts plain JSON and also handles common model response formats where JSON is wrapped in a code fence or surrounded by explanatory text. If no JSON object can be found, the command exits with a clear error message.

### 8. Output Format

The JSON artifact follows the Policy Passport shape used by the web proof of concept. It includes the Passport version, company name, policy name, effective scope, rule list, behavioral instruction, and plain language summary.

Each rule is normalized with a stable identifier, category, severity, rule text, violation examples, compliant examples, and an action. Invalid severity values are converted to `MEDIUM`. Invalid action values are converted to `WARN`.

The text artifact is designed for portability. It contains a readable header, the scoped rule list, the expected AI behavior, and a closing marker. This makes it suitable for direct use in AI assistant instructions or as an artifact inside an agent project.

### 9. Error Handling

The tool exits with a non zero status code when input is missing, the network request fails, the endpoint returns an error, or the model response cannot be parsed as JSON.

For troubleshooting, use the raw response option during generation:

```bash
python3 grc2prompt.py generate policy.txt --yes --raw-out rawresponse.txt --json-out passport.json --text-out passport.txt
```

The raw response file helps determine whether a failure came from the endpoint, the model output, or JSON parsing.

### 10. Recommended Workflow

Start with a small synthetic policy that contains five to twenty clear rules. Generate the JSON and text artifacts, review the extracted rules, and adjust the source policy if the model output is too broad or too vague. Once the output quality is acceptable, repeat the process with a sanitized representative policy sample.

For production planning, treat this command line tool as a reference implementation. The next technical step should be provider configuration, enterprise authentication, audit logging, deterministic output checks, and a controlled approval process before any generated Passport is deployed into a real AI environment.


## The Problem

Generative AI is being deployed inside enterprises at a pace that most GRC teams simply weren't ready for. The tools are useful, developers adopt them fast, and the security and compliance functions are left trying to retrofit controls onto workflows that already exist. 

The core issue is structural: large language models have no inherent knowledge of your organization's internal policies. An employee using ChatGPT to draft a client proposal has no guardrail preventing them from pasting in personal data. An AI agent autonomously processing support tickets has no built-in understanding of your data classification policy. The model is stateless with respect to your organizational context — every session starts from zero.

Current mitigation strategies fall into two camps. The first is technical integration: connecting AI infrastructure to policy engines like Open Policy Agent (OPA), implementing API gateways with inline policy enforcement, or fine-tuning models on internal documents. These approaches work, but they require significant engineering effort, dedicated infrastructure, and typically only cover one AI platform at a time. The second camp is user training — teaching employees what they should and shouldn't do. That approach relies entirely on human memory and good intentions, which is not a compliance strategy.

Policy Passport sits between these two extremes. It's not a full enterprise policy enforcement platform, and it's not a training pamphlet. It's a portable, LLM-native representation of your organizational policies that works with any major AI model, requires no infrastructure, and can be enforced centrally using controls that most AI providers already expose to enterprise administrators.

---

## Core Concept: The Policy Passport Format

A Policy Passport is a structured, natural-language artifact that encodes organizational GRC policies in a format optimized for LLM comprehension and runtime enforcement.

The format has three layers:

**1. Machine-Readable Rule Set**  
Individual rules are structured with explicit metadata: a unique identifier, a functional category (Data Handling, Access Control, Communication, Finance, Legal, IT Operations), a severity classification (CRITICAL / HIGH / MEDIUM / LOW), the rule itself expressed as a single enforceable statement, concrete violation and compliance examples, and a prescribed response action (BLOCK / WARN / LOG).

**2. Behavioral Instruction Block**  
A short, direct instruction set that tells the LLM exactly how to behave when it detects a policy conflict. This is not a suggestion — it's phrased as a system-level directive. The LLM is instructed to refuse, warn, or flag depending on the severity of the violation.

**3. Scope and Context Header**  
Identifies which organizational unit, system, data category, or process the policy applies to. This allows a single deployment to contain multiple passports with non-overlapping scopes, avoiding false positives.

The output is plain text — no proprietary format, no binary encoding, no platform dependencies. It can be read by a human, pasted into a chat window, injected as a system prompt via API, or stored as a file and referenced by an AI agent. This universality is intentional. The moment the format requires a specific runtime to function, its utility is limited. A plain text standard that works everywhere is more resilient than a sophisticated solution that works in one place.

---

## Architecture

### Generation Pipeline

```
[Source Policy Document]
         │
         ▼
[Policy Passport Generator]
   - LLM-based extraction
   - Rule normalization
   - Severity classification
   - Example generation
         │
         ▼
[Policy Passport Artifact]
   - Structured rule set (JSON internal)
   - Plain text export (universal)
   - Platform-specific deployment guides
```

The generator itself is LLM-powered. The input can be any prose policy document — a Word file, a Confluence page, a PDF, a plain text email chain that constitutes de facto policy. The model extracts individual rules, classifies them, generates behavioral examples, and outputs a normalized passport artifact.

This is where most of the real work happens. Going from "Employees must not share confidential customer data with unauthorized parties" to a structured rule with a clear violation example, a compliant example, and a severity rating requires contextual reasoning that rule-based extraction can't reliably do. An LLM handles this well.

### Deployment Architecture (No-Code Path)

For organizations that don't want to touch API infrastructure, the deployment path is:

1. Paste source policy into the Policy Passport Generator web tool
2. Export the plain text passport artifact
3. Deploy to target AI platforms using the platform's native administrative controls (detailed below)

This entire workflow requires no developer involvement. A GRC analyst or security administrator can do it end-to-end.

### Deployment Architecture (Programmatic Path)

For AI agents, automated workflows, and API-based deployments:

```python
# Minimal integration example
import anthropic

with open("data_handling_passport.txt") as f:
    passport = f.read()

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    system=f"{passport}\n\nYou are an assistant. Apply the Policy Passport above to all responses.",
    messages=[{"role": "user", "content": user_prompt}]
)
```

The passport is injected at the system prompt level, which gives it the highest instruction priority in the model's context hierarchy. User messages cannot override a system-level directive without explicit system-prompt permission — this is a property of how RLHF-trained instruction-following models process multi-turn context.

---

## Enterprise-Wide Enforcement

This is the part most concept documents skip over. Generating a passport is straightforward. The harder question is: how do you make sure every employee on every platform actually uses it?

The answer is that all four major enterprise AI platforms expose administrative controls that allow centralized policy injection. None of them require custom integrations to use.

---

### Quickest Win: ChatGPT Projects — Zero-Code Enforcement in Under 5 Minutes

Before covering the full enterprise admin paths, it's worth highlighting the fastest possible deployment for teams that need something working today. **ChatGPT Projects** (available on Teams and Enterprise plans, as well as ChatGPT Plus) let a team lead or admin create a shared project workspace with persistent instructions that apply to every conversation inside it. No admin portal access required. No IT ticket. No API.

Here's what this looks like in practice.

**Step 1. Create a Project and paste the Policy Passport into the "Hinweise" (Instructions) field:**


<img width="514" height="907" alt="Bildschirmfoto 2026-06-01 um 13 09 19" src="https://github.com/user-attachments/assets/052c19f5-c986-4e1c-8452-c0f6f7047d65" />

ChatGPT Project Settings with Policy Passport injected as instructions

The passport is placed verbatim into the project's instruction field. Every member of the project now has the policy active on every conversation silently, persistently, and without any action on their part.

**Step 2. A user submits a prompt that violates the policy:**

The user in this example asked ChatGPT to help write an email, but included a real person's name, a company email address, and account credentials in the prompt — a textbook GDPR / data handling violation.


<img width="1073" height="604" alt="Bildschirmfoto 2026-06-01 um 13 08 48" src="https://github.com/user-attachments/assets/1dbe65fa-150e-4c47-b272-1561e23d60bb" />

ChatGPT enforcing the Policy Passport, refusing to process personal data

ChatGPT declined to process the request, explained specifically what data triggered the policy (names, email addresses, account credentials), offered a compliant reformulation of the request, and separately addressed the password request by redirecting to the official IAM process. The model didn't just block — it was constructive. That's the behavioral instruction block in the passport doing its job.

No developer was involved. No API was called. An administrator created a project, pasted a text block, and the policy was enforced in the next conversation.

**When to use this approach:**  
ChatGPT Projects are the right starting point for teams with no dedicated AI infrastructure, for pilot deployments where you want to test passport behavior before committing to org-wide rollout, and for scope-specific use cases where a single team needs a policy that doesn't apply to the rest of the organization.

**Limitation to be aware of:**  
Project-level enforcement only covers conversations within that project. Users can open a new chat outside the project and the passport won't apply. For organization-wide coverage without exceptions, the admin-level deployment paths below are required.

---

### OpenAI / ChatGPT (Enterprise & Teams)

OpenAI's enterprise product exposes a **Custom Instructions** management interface at the workspace level. An admin can set organization-wide system prompts that are prepended to every conversation in the workspace. Individual users cannot override or disable these instructions.

**Enforcement path:**  
`ChatGPT Admin Portal → Settings → Custom Instructions → Organization Policy`

Paste the Policy Passport into the organization-level custom instructions field. Every conversation in the workspace will receive the passport as a persistent context injection. Users see no indication of this unless the administrator enables transparency notifications. The project-level example above demonstrates exactly what this enforcement looks like from the user's perspective the org-level setting applies the same mechanism across the entire workspace automatically.

For API users within the organization, the passport should be injected at the system prompt level in the API wrapper or AI gateway layer (see Gateway Enforcement below).

**Relevant documentation:** OpenAI Enterprise Admin Guide, Workspace Management section.

### Anthropic / Claude (Teams & Enterprise)

Claude's enterprise product supports **Organization System Prompts** configured at the workspace level via the admin dashboard. These prompts are injected before every conversation and cannot be modified by end users.

Additionally, Claude supports **Projects** persistent conversation containers with their own system prompt context. For team-level enforcement (e.g., the security team's Claude Project has the security policy passport, HR's Project has the HR data policy passport), Projects provide scope-appropriate guardrails without requiring a single monolithic policy block for all users.

**Enforcement path:**  
`Claude Admin Console → Organization → System Prompt → [Paste Policy Passport]`

Or at project level:  
`Claude.ai → Project Settings → Instructions → [Paste Passport]`

### Google / Gemini (Workspace Business/Enterprise)

Google exposes policy controls through **Gemini for Google Workspace** settings in the Google Admin Console. Administrators can configure data governance settings, restrict what information Gemini can access and process, and inject organizational context via the **Gemini App Configuration** panel.

For structured policy injection, the most reliable mechanism is configuring a **Gems** (custom Gemini agents) at the organizational level with the Policy Passport embedded in the agent's system instructions. The Gem can then be set as the default workspace assistant, effectively making the passport a persistent context for all Gemini usage.

**Enforcement path:**  
`Google Admin Console → Apps → Google Workspace → Gemini → Gems Management → [Create Org-Level Gem with Passport]`

For Gemini API users, injection follows the same system prompt pattern as other providers.

### Microsoft / Copilot (M365 Business/Enterprise)

Microsoft Copilot enforcement is the most granular of the four, reflecting M365's existing enterprise administration infrastructure.

**Copilot Studio** allows administrators to build custom Copilot agents with embedded system instructions and deploy them organizationwide through the M365 Admin Center. A Policy Passport embedded in a Copilot Studio agent's topic configuration will enforce the policy across all interactions with that agent.

For Microsoft 365 Copilot (the assistant integrated into Word, Teams, Outlook), admins can configure **Copilot Prompt Guidelines** via the Copilot Admin Center, which injects organizational context into Copilot interactions across M365 apps.

**Enforcement path:**  
`M365 Admin Center → Copilot → Settings → Prompt Guidelines → [Paste Passport]`  
or  
`Copilot Studio → Agents → New Agent → System Instructions → [Paste Passport]`

**Note on DLP integration:** Microsoft's Copilot enforcement integrates with existing Microsoft Purview Data Loss Prevention policies. Organizations already using Purview DLP can layer Policy Passport enforcement on top of existing data classification and protection controls, which gives them defense in depth at both the data layer and the model interaction layer.

### AI Gateway Enforcement (Platform-Agnostic)

For organizations that route LLM traffic through an AI gateway — Portkey, LiteLLM Proxy, AWS Bedrock, Azure AI Foundry, or a self-built proxy — the Policy Passport can be enforced at the gateway layer regardless of which model the end user is accessing.

The gateway intercepts each request, prepends the appropriate passport to the system prompt, and forwards to the target model. This approach has two advantages: it works across all models simultaneously, and it's invisible to the end user.

```python
# Gateway middleware example (simplified)
def inject_passport(request, passport_store):
    scope = classify_request_scope(request)  # e.g., "data_handling", "communication"
    passport = passport_store.get(scope)
    if passport:
        request.system = f"{passport}\n\n{request.system or ''}"
    return request
```

Tools like **Guardrails AI** and **LlamaGuard** can supplement this by adding post-generation validation, checking the model's output against policy rules after generation, before delivery to the user. This provides a second enforcement layer for high severity rules where BLOCK action is required.

---

## Security Considerations

**Prompt Injection**  
Policy Passports are injected at the system prompt level, but adversarial user inputs can attempt to override them ("ignore previous instructions"). The current design relies on the model's RLHF-trained instruction hierarchy to resist these attacks, which is not a hard security boundary. For CRITICAL-severity rules, gateway-level post-generation validation (OPA or Guardrails AI) provides a harder enforcement point that is not subject to prompt injection.

**Passport Integrity**  
A Policy Passport stored as a text file in an uncontrolled location can be modified by anyone with write access. Passport artifacts should be stored in version-controlled repositories with branch protection, treated as compliance artifacts with the same access controls as the source policy documents.

**Confidentiality of Policy Content**  
In some cases, the policy rules themselves may contain sensitive information (e.g., specific thresholds, counterparty names, regulatory references). Passport artifacts should be reviewed to ensure they don't expose information to users who would not otherwise have access to the underlying policy documents.

**Scope Contamination**  
A single large passport covering all organizational policies creates false positives. A rule about financial data handling should not trigger on a developer asking about code review. Passports should be scoped to specific user groups, use cases, or project contexts. The deployment mechanisms above all support this Projects in Claude, Gems in Gemini, and Copilot Studio agents in M365 all allow scope-specific policy injection.

---

## Roadmap

The current proof of concept addresses the generation and formatting problem. The following phases address enforcement, audit, and scalability.

**v1.0 — Generation (current)**  
Web-based generator tool. Accepts free-text policy input, outputs a structured Policy Passport artifact with platform-specific deployment instructions.

**v2.0 — Versioning & Audit Trail**  
Git-native passport versioning. Each passport is a tracked artifact with a changelog. When a source policy changes, the corresponding passport is flagged for regeneration. Audit log of deployments: which passport version was active at what time, on which platforms.

**v3.0 — CLI & CI/CD Integration**  
`policy-passport` Integration with CI/CD pipelines so passport regeneration can be triggered automatically when policy documents change in a document management system.

**v4.0 — Violation Telemetry**  
Instrumented passport format that includes a logging endpoint. When an LLM detects a violation and the action is LOG or WARN, the event is sent to a central telemetry service. This provides GRC teams with visibility into how often policy rules are being triggered, by which teams, and on what prompt categories — without logging the actual prompt content.

---

## Compatibility

| Platform | Admin Enforcement | API Injection | Manual (Copy/Paste) |
|---|---|---|---|
| ChatGPT (OpenAI) | ✓ Workspace Custom Instructions | ✓ System Prompt | ✓ |
| Claude (Anthropic) | ✓ Org System Prompt / Projects | ✓ System Prompt | ✓ |
| Gemini (Google) | ✓ Admin Console / Gems | ✓ System Instruction | ✓ |
| Copilot (Microsoft) | ✓ M365 Admin / Copilot Studio | ✓ System Prompt | ✓ |
| Open-source models | Via gateway layer | ✓ System Prompt | ✓ |

---

## Contributing

This is an early stage concept. Issues and pull requests are open. The areas that need the most work are prompt injection resistance, passport schema validation, and the violation telemetry specification.

If you're working on AI governance, LLM security, or enterprise GRC tooling and want to talk through the approach, open an issue or get in touch via my [Website](https://ozel0t-g.github.io/)

---

## References

- [NIST AI Risk Management Framework (AI RMF 1.0)](https://airc.nist.gov/RMF)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs/latest/)
- [Guardrails AI](https://github.com/guardrails-ai/guardrails)
- [Anthropic Constitutional AI](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)
- [ISO/IEC 42001:2023 — AI Management Systems](https://www.iso.org/standard/81230.html)
