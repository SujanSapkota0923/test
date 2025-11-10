// Reusable lightweight client-side search functionality
function initPageSearch(searchInputId, tableId, clearBtnSelector) {
	document.addEventListener('DOMContentLoaded', function() {
		const searchInput = document.getElementById(searchInputId);
		const clearBtn = document.querySelector(clearBtnSelector || '.clear-search');
		const table = document.getElementById(tableId);

		if (!searchInput || !table) return;

		searchInput.addEventListener('input', function() {
			const query = this.value.toLowerCase().trim();
			if (clearBtn) clearBtn.hidden = !query;

			const rows = table.querySelectorAll('tbody tr:not(.no-results)');
			let visibleCount = 0;

			rows.forEach(row => {
				const text = row.textContent.toLowerCase();
				const isVisible = text.includes(query);
				row.style.display = isVisible ? '' : 'none';
				if (isVisible) visibleCount++;
			});

			// Handle no results message if exists
			const noResultsRow = table.querySelector('tbody tr.no-results');
			if (noResultsRow) {
				noResultsRow.classList.toggle('d-none', visibleCount > 0);
			}
		});

		if (clearBtn) {
			clearBtn.addEventListener('click', function() {
				searchInput.value = '';
				searchInput.dispatchEvent(new Event('input'));
				searchInput.focus();
			});
		}
	});
}
