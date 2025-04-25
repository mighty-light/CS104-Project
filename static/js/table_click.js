let asc = true;
let lastColIdx = null;
let lastVal = null;

const getCellValue = (row, idx) => row.children[idx].textContent.trim();

document.addEventListener("DOMContentLoaded", () => {
    const table = document.querySelector("table");
    if (!table) return;
  
    const headers = Array.from(table.querySelectorAll("th")); // Headings
    const tbody = table.querySelector("tbody"); // Data
    const rows = Array.from(tbody.querySelectorAll("tr"));

  
    headers.forEach((header, colIdx) => {
        header.style.cursor = "pointer";
        header.addEventListener("click", () => {
    
            rows.sort((a, b) => {
                const aVal = getCellValue(a, colIdx);
                const bVal = getCellValue(b, colIdx);

                const aNum = parseFloat(aVal.replace(/,/g, ""));
                const bNum = parseFloat(bVal.replace(/,/g, ""));
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return aNum - bNum;
                }

                const alphaNumRe = /^([A-Za-z]+)(\d+)$/;
                const aMatch = aVal.match(alphaNumRe);
                const bMatch = bVal.match(alphaNumRe);

                if (aMatch && bMatch && aMatch[1] === bMatch[1]) {
                    return parseInt(aMatch[2], 10) - parseInt(bMatch[2], 10);
                }

                return aVal.localeCompare(bVal);
            });
  
            if (!asc) rows.reverse();
            asc = !asc;
    
            tbody.innerHTML = "";
            rows.forEach(row => tbody.appendChild(row));
    
            headers.forEach(h => h.textContent = h.textContent.replace(/[↕↑↓]$/, ""));
            header.textContent += asc ? " ↑" : " ↓";
        });
    });

    rows.forEach(row => {
        row.style.cursor = "pointer";
        row.addEventListener("click", (e) => {
          const cell = e.target.closest('td');
          if (!cell) return;
      
          const colIdx     = cell.cellIndex;
          const clickedVal = cell.textContent.trim();
      
          // If user clicked the same cell‐value again, clear filter
          if (colIdx === lastColIdx && clickedVal === lastVal) {
            rows.forEach(r => r.style.display = "");
            lastColIdx = null;
            lastVal = null;
            return;
          }
      
          // Otherwise apply new filter
          rows.forEach(r => {
            const rCell = r.children[colIdx];
            const val = rCell ? rCell.textContent.trim() : null;
            r.style.display = (val === clickedVal) ? "" : "none";
          });
      
          // remember for toggle
          lastColIdx = colIdx;
          lastVal = clickedVal;
        });
    });
});
  