
console.log("DOCUMIND AI STUDY ASSISTANT LOADED");

document.addEventListener("DOMContentLoaded", () => {
    const uploadButton = document.getElementById("uploadButton");
    const generateButton = document.getElementById("generateButton");
    const askButton = document.getElementById("askButton");

    const fileInput = document.getElementById("pdfFile");
    const fileName = document.getElementById("fileName");

    const uploadStatus = document.getElementById("uploadStatus");
    const generateStatus = document.getElementById("generateStatus");

    const summary = document.getElementById("summary");
    const questions = document.getElementById("questions");

    const questionInput = document.getElementById("question");
    const answer = document.getElementById("answer");
    const sources = document.getElementById("sources");

    if (
        !uploadButton ||
        !generateButton ||
        !askButton ||
        !fileInput ||
        !fileName ||
        !uploadStatus ||
        !generateStatus ||
        !summary ||
        !questions ||
        !questionInput ||
        !answer ||
        !sources
    ) {
        console.error("Required HTML elements are missing.");
        return;
    }

    let isUploading = false;
    let isGenerating = false;
    let isAsking = false;
    let documentReady = false;

    // ---------------------------------
    // Helpers
    // ---------------------------------

    function setStatus(element, message, type = "") {
        element.textContent = message;
        element.className = "status-message";

        if (type) {
            element.classList.add(type);
        }
    }

    function setButtonLoading(
        button,
        loading,
        loadingText,
        normalText
    ) {
        button.disabled = loading;

        const label = button.querySelector("span");

        if (label) {
            label.textContent = loading ? loadingText : normalText;
        }
    }

    async function readResponse(response) {
        const contentType = response.headers.get("content-type") || "";

        if (contentType.includes("application/json")) {
            return await response.json();
        }

        const text = await response.text();

        return {
            error: text || `Request failed with status ${response.status}.`
        };
    }

    function renderText(container, text) {
        // textContent avoids interpreting model output as HTML.
        container.textContent = text || "No content was returned.";
    }

    function resetStudyResults() {
        renderText(
            summary,
            "Your summary will appear here after generation."
        );

        renderText(
            questions,
            "Your practice questions will appear here after generation."
        );

        renderText(answer, "Your answer will appear here.");
        renderText(sources, "Sources will appear after your first question.");

        setStatus(generateStatus, "");
    }

    // ---------------------------------
    // PDF selection
    // ---------------------------------

    fileInput.addEventListener("change", () => {
        const file = fileInput.files[0];

        if (!file) {
            fileName.textContent = "No file selected";
            return;
        }

        const isPdf =
            file.type === "application/pdf" ||
            file.name.toLowerCase().endsWith(".pdf");

        if (!isPdf) {
            fileInput.value = "";
            fileName.textContent = "No file selected";

            setStatus(uploadStatus, "Please select a PDF file.", "error");
            return;
        }

        fileName.textContent = file.name;
        setStatus(uploadStatus, "");

        // A newly selected file is not ready until it is uploaded.
        documentReady = false;
        generateButton.disabled = true;
    });

    // ---------------------------------
    // Upload PDF
    // POST /upload
    // ---------------------------------

    uploadButton.addEventListener("click", async () => {
        if (isUploading) return;

        const file = fileInput.files[0];

        if (!file) {
            setStatus(uploadStatus, "Please select a PDF first.", "error");
            return;
        }

        const isPdf =
            file.type === "application/pdf" ||
            file.name.toLowerCase().endsWith(".pdf");

        if (!isPdf) {
            setStatus(uploadStatus, "Only PDF files are supported.", "error");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        isUploading = true;
        documentReady = false;
        generateButton.disabled = true;

        setStatus(
            uploadStatus,
            "Uploading PDF and building the search database...",
            "loading"
        );

        setButtonLoading(
            uploadButton,
            true,
            "Processing document...",
            "Upload document"
        );

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            const data = await readResponse(response);

            if (!response.ok) {
                throw new Error(data.error || "PDF upload failed.");
            }

            documentReady = true;
            generateButton.disabled = false;

            setStatus(
                uploadStatus,
                data.message || "PDF processed successfully.",
                "success"
            );

            resetStudyResults();

            renderText(
                answer,
                "Your document is ready. You can generate study material or ask a question."
            );

            questionInput.focus();

        } catch (error) {
            console.error("UPLOAD ERROR:", error);

            documentReady = false;
            generateButton.disabled = true;

            setStatus(
                uploadStatus,
                error.message || "Could not upload the PDF.",
                "error"
            );
        } finally {
            isUploading = false;

            setButtonLoading(
                uploadButton,
                false,
                "Processing document...",
                "Upload document"
            );
        }
    });

    // ---------------------------------
    // Generate summary and questions
    // POST /generate-study-material
    // ---------------------------------

    generateButton.addEventListener("click", async () => {
        if (isGenerating || !documentReady) return;

        isGenerating = true;

        setButtonLoading(
            generateButton,
            true,
            "Generating study material...",
            "✦ Generate Summary & Questions"
        );

        setStatus(
            generateStatus,
            "Analyzing the document. This may take a little while...",
            "loading"
        );

        renderText(summary, "Generating summary...");
        renderText(questions, "Generating important questions...");

        try {
            const response = await fetch("/generate-study-material", {
                method: "POST"
            });

            const data = await readResponse(response);

            if (!response.ok) {
                throw new Error(
                    data.error || "Could not generate study material."
                );
            }

            renderText(summary, data.summary);
            renderText(questions, data.questions);

            setStatus(
                generateStatus,
                "Summary and questions generated successfully.",
                "success"
            );

        } catch (error) {
            console.error("GENERATION ERROR:", error);

            renderText(
                summary,
                "Summary generation failed. Please try again."
            );

            renderText(
                questions,
                "Question generation failed. Please try again."
            );

            setStatus(
                generateStatus,
                error.message || "Could not generate study material.",
                "error"
            );
        } finally {
            isGenerating = false;

            setButtonLoading(
                generateButton,
                false,
                "Generating study material...",
                "✦ Generate Summary & Questions"
            );

            generateButton.disabled = !documentReady;
        }
    });

    // ---------------------------------
    // Ask question
    // POST /ask
    // ---------------------------------

    async function askQuestion() {
        if (isAsking) return;

        const question = questionInput.value.trim();

        if (!question) {
            renderText(answer, "Please enter a question first.");
            questionInput.focus();
            return;
        }

        isAsking = true;

        setButtonLoading(
            askButton,
            true,
            "Thinking...",
            "Ask question"
        );

        renderText(answer, "Searching your document for an answer...");
        renderText(sources, "Retrieving sources...");

        try {
            const response = await fetch("/ask", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ question })
            });

            const data = await readResponse(response);

            if (!response.ok) {
                throw new Error(data.error || "Question request failed.");
            }

            renderText(answer, data.answer);

            renderText(
                sources,
                Array.isArray(data.sources)
                    ? JSON.stringify(data.sources, null, 2)
                    : data.sources || "No sources were returned."
            );

        } catch (error) {
            console.error("ASK ERROR:", error);

            renderText(
                answer,
                error.message || "Unable to answer the question."
            );

            renderText(sources, "Sources are unavailable.");
        } finally {
            isAsking = false;

            setButtonLoading(
                askButton,
                false,
                "Thinking...",
                "Ask question"
            );
        }
    }

    askButton.addEventListener("click", askQuestion);

    questionInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && event.ctrlKey) {
            event.preventDefault();
            askQuestion();
        }
    });

    console.log("DOCUMIND AI READY");
});
