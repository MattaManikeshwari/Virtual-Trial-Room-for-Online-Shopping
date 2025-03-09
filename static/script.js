        document.addEventListener("DOMContentLoaded", function() {
            const shirtBtn = document.getElementById("shirt-btn");
            const pantBtn = document.getElementById("pant-btn");
            const dressBtn = document.getElementById("dress-btn");

            const shirtSection = document.getElementById("shirts-section");
            const pantSection = document.getElementById("pants-section");
            const dressSection = document.getElementById("dresses-section");

            shirtBtn.addEventListener("click", function() {
                shirtSection.classList.remove("hidden");
                pantSection.classList.add("hidden");
                dressSection.classList.add("hidden");

                shirtBtn.classList.add("text-purple-600", "bg-purple-50");
                pantBtn.classList.remove("text-purple-600", "bg-purple-50");
                dressBtn.classList.remove("text-purple-600", "bg-purple-50");
            });

            pantBtn.addEventListener("click", function() {
                pantSection.classList.remove("hidden");
                shirtSection.classList.add("hidden");
                dressSection.classList.add("hidden");

                pantBtn.classList.add("text-purple-600", "bg-purple-50");
                shirtBtn.classList.remove("text-purple-600", "bg-purple-50");
                dressBtn.classList.remove("text-purple-600", "bg-purple-50");
            });

            dressBtn.addEventListener("click", function() {
                dressSection.classList.remove("hidden");
                shirtSection.classList.add("hidden");
                pantSection.classList.add("hidden");

                dressBtn.classList.add("text-purple-600", "bg-purple-50");
                shirtBtn.classList.remove("text-purple-600", "bg-purple-50");
                pantBtn.classList.remove("text-purple-600", "bg-purple-50");
            });
        });