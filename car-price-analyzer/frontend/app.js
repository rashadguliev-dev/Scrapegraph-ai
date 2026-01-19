document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // UI Elements
    const btn = document.getElementById('searchBtn');
    const spinner = document.getElementById('spinner');
    const resultsArea = document.getElementById('resultsArea');
    const progress = document.getElementById('progress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const errorBox = document.getElementById('error');

    // Reset UI
    resultsArea.classList.add('hidden');
    errorBox.classList.add('hidden');
    progress.classList.remove('hidden');
    btn.disabled = true;
    btn.classList.add('opacity-75');
    spinner.classList.remove('hidden');

    // Animate Progress (Fake)
    let percent = 0;
    const interval = setInterval(() => {
        if(percent < 90) {
            percent += Math.random() * 5;
            if(percent > 90) percent = 90;
            progressBar.style.width = percent + '%';
            document.getElementById('progressPercent').innerText = Math.round(percent) + '%';
        }
    }, 500);

    // Get Data
    const make = document.getElementById('make').value;
    const model = document.getElementById('model').value;
    const year_min = document.getElementById('year_min').value;
    const year_max = document.getElementById('year_max').value;

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                make, model, year_min: parseInt(year_min), year_max: parseInt(year_max)
            })
        });

        const data = await response.json();

        // Complete Progress
        clearInterval(interval);
        progressBar.style.width = '100%';
        document.getElementById('progressPercent').innerText = '100%';

        if (data.results && data.results.length > 0) {
            renderResults(data.results);
            setTimeout(() => {
                progress.classList.add('hidden');
                resultsArea.classList.remove('hidden');
            }, 500);
        } else {
            throw new Error("No cars found or API error.");
        }

    } catch (err) {
        clearInterval(interval);
        progress.classList.add('hidden');
        errorBox.classList.remove('hidden');
        document.getElementById('errorMessage').innerText = err.message || "Failed to fetch data.";
    } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-75');
        spinner.classList.add('hidden');
    }
});

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: currency }).format(amount);
}

function renderResults(results) {
    const tbody = document.getElementById('resultsTableBody');
    tbody.innerHTML = '';

    // Sort by Total Landed Cost (Ascending)
    // Filter out UAE for sorting to find best import deals
    const imports = results.filter(r => r.source_country !== 'UAE').sort((a, b) => a.financials.total_usd - b.financials.total_usd);
    const uaeOffers = results.filter(r => r.source_country === 'UAE');

    // Calculate UAE Average
    let uaeAvg = 0;
    if (uaeOffers.length > 0) {
        uaeAvg = uaeOffers.reduce((acc, curr) => acc + curr.financials.total_usd, 0) / uaeOffers.length;
    }

    // Render Cards
    if (imports.length > 0) {
        const best = imports[0];
        updateCard('cardWinner', 'winner', best, uaeAvg);

        if (imports.length > 1) {
            updateCard('cardSecond', 'second', imports[1], uaeAvg);
        } else {
             document.getElementById('cardSecond').classList.add('hidden');
        }
    } else {
        document.getElementById('cardWinner').classList.add('hidden');
        document.getElementById('cardSecond').classList.add('hidden');
    }

    if (uaeAvg > 0) {
        document.getElementById('uaePrice').innerText = formatCurrency(uaeAvg); // Approx base
        document.getElementById('uaeTotal').innerText = formatCurrency(uaeAvg); // Total same as base for local
        document.getElementById('cardUAE').classList.remove('hidden');
    } else {
        document.getElementById('cardUAE').classList.add('hidden');
    }

    // Render Table
    // Merge all and sort
    const allSorted = [...results].sort((a, b) => a.financials.total_usd - b.financials.total_usd);

    allSorted.forEach(car => {
        const tr = document.createElement('tr');

        const isUAE = car.source_country === 'UAE';
        const savings = uaeAvg > 0 ? (uaeAvg - car.financials.total_usd) : 0;
        const savingsPct = uaeAvg > 0 ? (savings / uaeAvg * 100) : 0;

        let savingsHtml = '-';
        if (!isUAE && uaeAvg > 0) {
            const color = savings > 0 ? 'text-green-600' : 'text-red-600';
            const sign = savings > 0 ? '-' : '+';
            savingsHtml = `<span class="${color} font-bold">${sign}${Math.abs(savingsPct).toFixed(1)}%</span>`;
        }

        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                    <div class="ml-0">
                        <div class="text-sm font-medium text-gray-900">${getFlag(car.source_country)} ${car.source_country}</div>
                        <div class="text-xs text-gray-500">${new URL(car.site).hostname}</div>
                    </div>
                </div>
            </td>
            <td class="px-6 py-4">
                <div class="text-sm text-gray-900">${car.year} ${car.model}</div>
                <div class="text-xs text-gray-500">${car.mileage || '?'}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                ${formatCurrency(car.price, car.currency)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                 <div class="text-xs">
                    Shipping: ${formatCurrency(car.financials.shipping_usd)}<br>
                    VAT: ${formatCurrency(car.financials.vat_usd)}
                 </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                ${formatCurrency(car.financials.total_usd)}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                ${savingsHtml}
            </td>
             <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <a href="${car.link}" target="_blank" class="text-blue-600 hover:text-blue-900">Link</a>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateCard(cardId, prefix, car, uaeAvg) {
    document.getElementById(cardId).classList.remove('hidden');
    document.getElementById(prefix + 'Country').innerText = `${getFlag(car.source_country)} ${car.source_country} (${car.year})`;
    document.getElementById(prefix + 'BasePrice').innerText = formatCurrency(car.price, car.currency);
    document.getElementById(prefix + 'Total').innerText = formatCurrency(car.financials.total_usd);

    if (uaeAvg > 0) {
        const savings = uaeAvg - car.financials.total_usd;
        if (savings > 0) {
             document.getElementById(prefix + 'Savings').innerText = `Save ${formatCurrency(savings)}`;
             document.getElementById(prefix + 'Savings').className = "bg-green-100 text-green-800 px-2 py-1 rounded text-xs font-bold";
        } else {
             document.getElementById(prefix + 'Savings').innerText = `More expensive`;
             document.getElementById(prefix + 'Savings').className = "bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-bold";
        }
    } else {
         document.getElementById(prefix + 'Savings').innerText = '';
    }
}

function getFlag(country) {
    const flags = {
        'UAE': '🇦🇪',
        'USA': '🇺🇸',
        'Japan': '🇯🇵',
        'Korea': '🇰🇷',
        'China': '🇨🇳',
        'Europe': '🇪🇺',
        'Germany': '🇩🇪'
    };
    return flags[country] || '🌍';
}
