(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const buttons = Array.from(document.querySelectorAll("[data-topic-filter]"));
        const cards = Array.from(document.querySelectorAll(".archive-card"));
        if (!buttons.length || !cards.length) {
            return;
        }

        function setFilter(topic) {
            buttons.forEach((button) => {
                button.classList.toggle("active", button.dataset.topicFilter === topic);
            });

            cards.forEach((card) => {
                const rawTopics = card.dataset.topics || "";
                const topics = rawTopics.split(",").filter(Boolean);
                const visible = topic === "all" || topics.includes(topic);
                card.dataset.topicState = visible ? "visible" : "hidden";
            });
        }

        buttons.forEach((button) => {
            button.addEventListener("click", function () {
                setFilter(button.dataset.topicFilter || "all");
            });
        });

        setFilter("all");
    });
})();
