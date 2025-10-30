document.addEventListener('DOMContentLoaded', function () {
    // Check if the screen is small (mobile)
    if (window.innerWidth < 768) {
        const categoryItems = document.querySelectorAll('.category-menu .category-item');

        categoryItems.forEach(item => {
            // Prevent the default link behavior on the first click
            const link = item.querySelector('a');
            let firstClick = true;

            link.addEventListener('click', function (e) {
                // If the submenu exists and it's the first click, prevent navigation
                const submenu = item.querySelector('.brand-submenu');
                if (submenu && firstClick) {
                    e.preventDefault();

                    // Hide all other submenus
                    document.querySelectorAll('.brand-submenu.show').forEach(otherSubmenu => {
                        if (otherSubmenu !== submenu) {
                            otherSubmenu.classList.remove('show');
                        }
                    });

                    // Toggle the current submenu
                    submenu.classList.toggle('show');
                    firstClick = false; // The next click will follow the link
                } 
            });

            // Add a back button to submenus
            const submenu = item.querySelector('.brand-submenu');
            if (submenu) {
                const backButton = document.createElement('button');
                backButton.textContent = 'Back to Categories';
                backButton.classList.add('btn', 'btn-secondary', 'm-2');
                backButton.onclick = function() {
                    submenu.classList.remove('show');
                    firstClick = true; // Reset click behavior
                };
                submenu.prepend(backButton);
            }
        });

        // Add a new CSS rule for the mobile view
        const style = document.createElement('style');
        style.innerHTML = `
            .brand-submenu.show {
                display: block !important;
            }
        `;
        document.head.appendChild(style);
    }
});
