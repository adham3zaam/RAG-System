console.log("SCRIPT.JS LOADED");


document.addEventListener(
    "DOMContentLoaded",
    function () {

        console.log("DOM LOADED");


        // =========================
        // Elements
        // =========================

        const uploadButton =
            document.getElementById("uploadButton");

        const askButton =
            document.getElementById("askButton");

        const fileInput =
            document.getElementById("pdfFile");

        const uploadStatus =
            document.getElementById("uploadStatus");

        const questionInput =
            document.getElementById("question");

        const answer =
            document.getElementById("answer");

        const sources =
            document.getElementById("sources");


        // =========================
        // Check Elements
        // =========================

        console.log(
            "Upload button:",
            uploadButton
        );

        console.log(
            "Ask button:",
            askButton
        );

        console.log(
            "File input:",
            fileInput
        );


        // =========================
        // Upload PDF
        // =========================

        uploadButton.addEventListener(
            "click",
            async function () {

                console.log(
                    "UPLOAD BUTTON CLICKED"
                );


                if (!fileInput.files.length) {

                    uploadStatus.innerText =
                        "Please select a PDF file.";

                    return;
                }


                const file =
                    fileInput.files[0];


                console.log(
                    "Selected file:",
                    file.name
                );


                const formData =
                    new FormData();


                formData.append(
                    "file",
                    file
                );


                uploadStatus.innerText =
                    "Uploading PDF...";


                try {

                    console.log(
                        "Sending POST /upload"
                    );


                    const response =
                        await fetch(
                            "/upload",
                            {
                                method: "POST",
                                body: formData
                            }
                        );


                    console.log(
                        "Response status:",
                        response.status
                    );


                    const data =
                        await response.json();


                    console.log(
                        "Response data:",
                        data
                    );


                    if (response.ok) {

                        uploadStatus.innerText =
                            "PDF uploaded successfully. You can ask questions now.";

                    } else {

                        uploadStatus.innerText =
                            data.error ||
                            "Upload failed.";
                    }


                } catch (error) {

                    console.error(
                        "UPLOAD ERROR:",
                        error
                    );


                    uploadStatus.innerText =
                        "Server error.";
                }

            }
        );


        // =========================
        // Ask Question
        // =========================

        askButton.addEventListener(
            "click",
            async function () {

                console.log(
                    "ASK BUTTON CLICKED"
                );


                const question =
                    questionInput.value.trim();


                if (!question) {

                    answer.innerText =
                        "Please enter a question.";

                    return;
                }


                answer.innerText =
                    "Thinking...";


                sources.innerText =
                    "Loading sources...";


                try {

                    const response =
                        await fetch(
                            "/ask",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({
                                    question:
                                        question
                                })
                            }
                        );


                    const data =
                        await response.json();


                    console.log(
                        "Ask response:",
                        data
                    );


                    if (!response.ok) {

                        answer.innerText =
                            data.error ||
                            "Something went wrong.";

                        sources.innerText =
                            data.details || "";

                        return;
                    }


                    answer.innerText =
                        data.answer;


                    sources.innerText =
                        JSON.stringify(
                            data.sources,
                            null,
                            2
                        );

                } catch (error) {

                    console.error(
                        "ASK ERROR:",
                        error
                    );


                    answer.innerText =
                        "Server error.";

                    sources.innerText =
                        "";
                }

            }
        );

    }
);