// Main JavaScript file for CoC Statistics

document.addEventListener('DOMContentLoaded', function() {
    console.log('CoC Statistics app loaded');
    
    // Add sorting functionality to tables
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        let currentSortCol = null;
        let currentSortOrder = 'asc';

        headers.forEach((header, index) => {
            header.addEventListener('click', () => {
                // Remove sort classes from all headers
                headers.forEach(h => {
                    h.classList.remove('sort-asc', 'sort-desc');
                });

                // Determine sort order
                if (currentSortCol === index) {
                    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
                } else {
                    currentSortCol = index;
                    currentSortOrder = 'asc';
                }

                // Add sort class to current header
                header.classList.add(`sort-${currentSortOrder}`);

                // Get table rows and convert to array for sorting
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));

                // Sort rows
                rows.sort((a, b) => {
                    const aCol = a.querySelectorAll('td')[index];
                    const bCol = b.querySelectorAll('td')[index];
                    
                    let aValue = aCol.textContent.trim();
                    let bValue = bCol.textContent.trim();

                    // Handle league column with priority sorting
                    if (header.textContent.trim() === 'League') {
                        const leaguePriority = {
                            'Titan League I': 21, 'Titan League II': 20, 'Titan League III': 19,
                            'Champion League I': 18, 'Champion League II': 17, 'Champion League III': 16,
                            'Master League I': 15, 'Master League II': 14, 'Master League III': 13,
                            'Crystal League I': 12, 'Crystal League II': 11, 'Crystal League III': 10,
                            'Gold League I': 9, 'Gold League II': 8, 'Gold League III': 7,
                            'Silver League I': 6, 'Silver League II': 5, 'Silver League III': 4,
                            'Bronze League I': 3, 'Bronze League II': 2, 'Bronze League III': 1
                        };
                        const aPriority = leaguePriority[aValue] || 0;
                        const bPriority = leaguePriority[bValue] || 0;
                        return currentSortOrder === 'asc' ? aPriority - bPriority : bPriority - aPriority;
                    }

                    // Handle Town Hall level sorting
                    if (header.textContent.trim() === 'Town Hall') {
                        const aNum = parseInt(aValue.replace(/[^0-9]/g, '')) || 0;
                        const bNum = parseInt(bValue.replace(/[^0-9]/g, '')) || 0;
                        return currentSortOrder === 'asc' ? aNum - bNum : bNum - aNum;
                    }

                    // Handle role column with priority sorting
                    if (header.textContent.trim() === 'Role') {
                        const rolePriority = {
                            'Leader': 4,
                            'Coleader': 3,
                            'Admin': 2,
                            'Member': 1
                        };
                        const aPriority = rolePriority[aValue] || 0;
                        const bPriority = rolePriority[bValue] || 0;
                        return currentSortOrder === 'asc' ? aPriority - bPriority : bPriority - aPriority;
                    }

                    // Handle numeric columns
                    if (['Trophies', 'Exp Level', 'Clan Rank', 'Previous Rank', 'Donations', 'Donations Received'].includes(header.textContent.trim())) {
                        aValue = parseInt(aValue) || 0;
                        bValue = parseInt(bValue) || 0;
                        return currentSortOrder === 'asc' ? aValue - bValue : bValue - aValue;
                    }
                    
                    // Handle N/A values
                    if (aValue === 'N/A') aValue = '';
                    if (bValue === 'N/A') bValue = '';

                    // Text comparison
                    return currentSortOrder === 'asc' 
                        ? aValue.localeCompare(bValue)
                        : bValue.localeCompare(aValue);
                });

                // Reorder rows in the table
                rows.forEach(row => tbody.appendChild(row));
            });
        });
    });
});