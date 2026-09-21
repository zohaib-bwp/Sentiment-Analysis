// Sentiment Analyzer - Frontend Script with Chart.js
let sentimentChart = null;

document.addEventListener('DOMContentLoaded', () => {
    // Form elements
    const form = document.getElementById('predict-form');
    const fileForm = document.getElementById('file-predict-form');
    const batchForm = document.getElementById('batch-predict-form');
    const inputText = document.getElementById('input-text');
    const fileInput = document.getElementById('file-input-field');
    const batchFileInput = document.getElementById('batch-file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const batchFilesList = document.getElementById('batch-files-list');
    const resultDiv = document.getElementById('prediction-result');
    const spinner = document.getElementById('loading-spinner');
    const historyContainer = document.getElementById('history-container');
    const clearBtn = document.getElementById('clear-history');
    const exportCsvBtn = document.getElementById('export-csv');
    const scrollTopBtn = document.getElementById('scrollTop');

    // Initialize
    loadHistory();
    loadStats();

    // Scroll to top button functionality
    window.addEventListener('scroll', () => {
        if (scrollTopBtn) {
            if (window.pageYOffset > 300) {
                scrollTopBtn.classList.add('show');
            } else {
                scrollTopBtn.classList.remove('show');
            }
        }
    });

    if (scrollTopBtn) {
        scrollTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Display selected file name
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                fileNameDisplay.innerHTML = `<i class="fas fa-file"></i> Selected: <strong>${fileName}</strong>`;
                fileNameDisplay.style.color = 'white';
                fileNameDisplay.style.marginTop = '15px';
            } else {
                fileNameDisplay.innerHTML = '';
            }
        });
    }

    // Display batch files
    if (batchFileInput) {
        batchFileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            batchFilesList.innerHTML = '';

            if (files.length === 0) return;

            files.forEach((file, index) => {
                const item = document.createElement('div');
                item.style.cssText = `
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: 15px;
                    padding: 15px;
                    margin-top: 10px;
                    color: white;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                `;
                item.innerHTML = `
                    <div>
                        <i class="fas fa-file"></i> ${file.name}
                        <small style="opacity: 0.7; margin-left: 10px;">(${(file.size / 1024).toFixed(2)} KB)</small>
                    </div>
                    <button type="button" style="
                        background: linear-gradient(135deg, #f45c43, #eb3349);
                        border: none;
                        border-radius: 10px;
                        padding: 8px 15px;
                        color: white;
                        cursor: pointer;
                        font-size: 0.9rem;
                    " onclick="removeBatchFile(${index})">
                        <i class="fas fa-times"></i> Remove
                    </button>
                `;
                batchFilesList.appendChild(item);
            });
        });
    }

    // Remove batch file function
    window.removeBatchFile = function(index) {
        const dt = new DataTransfer();
        const files = Array.from(batchFileInput.files);

        files.forEach((file, i) => {
            if (i !== index) dt.items.add(file);
        });

        batchFileInput.files = dt.files;
        batchFileInput.dispatchEvent(new Event('change'));
    };

    // Text input form submission
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            resultDiv.innerHTML = '';
            spinner.style.display = 'block';

            const text = inputText.value.trim();
            if (!text) {
                spinner.style.display = 'none';
                showAlert('Please enter text to analyze', 'warning');
                return;
            }

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `Server error: ${response.status}`);
                }

                spinner.style.display = 'none';
                displayResult(data, text);
                loadHistory();
                loadStats();
                scrollToResult();

            } catch (error) {
                spinner.style.display = 'none';
                showAlert(error.message, 'danger');
                console.error('Analysis error:', error);
            }
        });
    }

    // File upload form submission
    if (fileForm) {
        fileForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            resultDiv.innerHTML = '';
            spinner.style.display = 'block';

            const file = fileInput.files[0];
            if (!file) {
                spinner.style.display = 'none';
                showAlert('Please select a file to analyze', 'warning');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/analyze_file', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `Server error: ${response.status}`);
                }

                spinner.style.display = 'none';
                displayResult(data, `File: ${file.name}`);
                loadHistory();
                loadStats();
                scrollToResult();

                fileInput.value = '';
                fileNameDisplay.innerHTML = '';

            } catch (error) {
                spinner.style.display = 'none';
                showAlert(error.message, 'danger');
                console.error('File analysis error:', error);
            }
        });
    }

    // Batch upload form submission
    if (batchForm) {
        batchForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            resultDiv.innerHTML = '';
            spinner.style.display = 'block';

            const files = batchFileInput.files;
            if (files.length === 0) {
                spinner.style.display = 'none';
                showAlert('Please select files to analyze', 'warning');
                return;
            }

            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }

            try {
                const response = await fetch('/analyze_batch', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `Server error: ${response.status}`);
                }

                spinner.style.display = 'none';
                displayBatchResults(data.results);
                loadHistory();
                loadStats();
                scrollToResult();

                batchFileInput.value = '';
                batchFilesList.innerHTML = '';

            } catch (error) {
                spinner.style.display = 'none';
                showAlert(error.message, 'danger');
                console.error('Batch analysis error:', error);
            }
        });
    }

    // Create Chart
    function createSentimentChart(posPercentage, negPercentage) {
        const chartId = 'sentiment-chart-' + Date.now();
        
        const chartHTML = `
            <div class="chart-container">
                <h4><i class="fas fa-chart-pie"></i> Sentiment Distribution</h4>
                <div class="chart-wrapper">
                    <canvas id="${chartId}"></canvas>
                </div>
            </div>
        `;
        
        // Insert chart container after stats row
        const resultCard = resultDiv.querySelector('.result-card');
        if (resultCard) {
            const statsRow = resultCard.querySelector('.stats-row');
            if (statsRow) {
                statsRow.insertAdjacentHTML('afterend', chartHTML);
                
                // Create chart after DOM is updated
                setTimeout(() => {
                    const ctx = document.getElementById(chartId);
                    if (ctx) {
                        // Destroy previous chart if exists
                        if (sentimentChart) {
                            sentimentChart.destroy();
                        }
                        
                        sentimentChart = new Chart(ctx, {
                            type: 'doughnut',
                            data: {
                                labels: ['Positive', 'Negative'],
                                datasets: [{
                                    data: [posPercentage, negPercentage],
                                    backgroundColor: [
                                        'rgba(56, 239, 125, 0.8)',
                                        'rgba(244, 92, 67, 0.8)'
                                    ],
                                    borderColor: [
                                        'rgba(56, 239, 125, 1)',
                                        'rgba(244, 92, 67, 1)'
                                    ],
                                    borderWidth: 2
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {
                                    legend: {
                                        position: 'bottom',
                                        labels: {
                                            padding: 20,
                                            font: {
                                                size: 14,
                                                family: "'Poppins', sans-serif",
                                                weight: '600'
                                            },
                                            color: '#333'
                                        }
                                    },
                                    tooltip: {
                                        callbacks: {
                                            label: function(context) {
                                                return context.label + ': ' + context.parsed.toFixed(1) + '%';
                                            }
                                        },
                                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                        titleFont: {
                                            size: 14,
                                            family: "'Poppins', sans-serif"
                                        },
                                        bodyFont: {
                                            size: 13,
                                            family: "'Poppins', sans-serif"
                                        },
                                        padding: 12,
                                        cornerRadius: 8
                                    }
                                },
                                animation: {
                                    animateRotate: true,
                                    animateScale: true,
                                    duration: 1000,
                                    easing: 'easeInOutQuart'
                                }
                            }
                        });
                    }
                }, 100);
            }
        }
    }

    // Display single result
    function displayResult(data, text) {
        const sentiment = data.sentiment || 'Unknown';
        const posPercentage = data.positive_percentage?.toFixed(1) || '0.0';
        const negPercentage = data.negative_percentage?.toFixed(1) || '0.0';
        const posCount = data.positive_count || 0;
        const negCount = data.negative_count || 0;
        const posWords = data.positive_words || [];
        const negWords = data.negative_words || [];

        let emoji = '🤔';
        if (sentiment.toLowerCase().includes('positive')) {
            emoji = '😊';
        } else if (sentiment.toLowerCase().includes('negative')) {
            emoji = '😞';
        }

        const resultId = 'result-' + Date.now();

        const resultHTML = `
            <div class="result-card">
                <div class="sentiment-emoji">${emoji}</div>
                <div class="sentiment-label">${sentiment}</div>
                
                <div class="stats-row">
                    <div class="stat-box">
                        <i class="fas fa-smile" style="color: #38ef7d;"></i>
                        <span class="stat-number-result">${posPercentage}%</span>
                        <span class="stat-label-result">Positive</span>
                        <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8; color: white;">
                            ${posCount} positive words
                        </div>
                    </div>
                    
                    <div class="stat-box">
                        <i class="fas fa-frown" style="color: #f45c43;"></i>
                        <span class="stat-number-result">${negPercentage}%</span>
                        <span class="stat-label-result">Negative</span>
                        <div style="margin-top: 10px; font-size: 0.9rem; opacity: 0.8; color: white;">
                            ${negCount} negative words
                        </div>
                    </div>
                </div>
                
                ${data.extracted_text_length ? `
                    <div style="margin-top: 20px; opacity: 0.9; color: white;">
                        <i class="fas fa-file-alt"></i> Analyzed ${data.extracted_text_length} characters
                    </div>
                ` : ''}
                
                <button class="btn-show-more" onclick="toggleKeywords('${resultId}')">
                    <i class="fas fa-chevron-down"></i> Show Keywords
                </button>
                
                <div id="${resultId}" class="keywords-section">
                    <div class="keyword-category">
                        <h5>
                            <i class="fas fa-smile" style="color: #38ef7d;"></i> 
                            Positive Keywords (${posCount})
                        </h5>
                        <div>
                            ${posWords.length > 0 ? posWords.map(word => 
                                `<span class="keyword-badge keyword-positive">${word}</span>`
                            ).join('') : '<span style="color: #666;">No positive keywords found</span>'}
                        </div>
                    </div>
                    
                    <div class="keyword-category">
                        <h5>
                            <i class="fas fa-frown" style="color: #f45c43;"></i> 
                            Negative Keywords (${negCount})
                        </h5>
                        <div>
                            ${negWords.length > 0 ? negWords.map(word => 
                                `<span class="keyword-badge keyword-negative">${word}</span>`
                            ).join('') : '<span style="color: #666;">No negative keywords found</span>'}
                        </div>
                    </div>
                </div>
            </div>
        `;

        resultDiv.innerHTML = resultHTML;
        
        // Create chart with animation
        createSentimentChart(parseFloat(posPercentage), parseFloat(negPercentage));
    }

    // Display batch results
    function displayBatchResults(results) {
        let html = `
            <div style="margin-top: 30px;">
                <h3 style="color: white; text-align: center; margin-bottom: 25px; text-shadow: 0 2px 10px rgba(0,0,0,0.2);">
                    <i class="fas fa-layer-group"></i> Batch Analysis Results
                </h3>
        `;

        results.forEach((result, index) => {
            if (result.error) {
                html += `
                    <div class="alert" style="
                        background: rgba(244, 92, 67, 0.2);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(244, 92, 67, 0.4);
                        border-radius: 20px;
                        padding: 20px;
                        margin-bottom: 15px;
                        color: white;
                    ">
                        <strong><i class="fas fa-exclamation-circle"></i> ${result.filename}</strong><br>
                        <span style="opacity: 0.9;">Error: ${result.error}</span>
                    </div>
                `;
            } else {
                const emoji = result.sentiment.toLowerCase().includes('positive') ? '😊' : '😞';
                const bgColor = result.sentiment.toLowerCase().includes('positive') 
                    ? 'rgba(56, 239, 125, 0.2)' 
                    : 'rgba(244, 92, 67, 0.2)';
                const borderColor = result.sentiment.toLowerCase().includes('positive') 
                    ? 'rgba(56, 239, 125, 0.4)' 
                    : 'rgba(244, 92, 67, 0.4)';
                
                html += `
                    <div class="alert" style="
                        background: ${bgColor};
                        backdrop-filter: blur(10px);
                        border: 1px solid ${borderColor};
                        border-radius: 20px;
                        padding: 20px;
                        margin-bottom: 15px;
                        color: white;
                    ">
                        <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 15px;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong style="font-size: 1.1rem;">${emoji} ${result.filename}</strong>
                                <p style="margin: 10px 0 5px 0; opacity: 0.9;">
                                    <strong>Sentiment:</strong> ${result.sentiment}
                                </p>
                                <small style="opacity: 0.8;">
                                    ✅ Positive: ${result.positive_percentage.toFixed(1)}% | 
                                    ❌ Negative: ${result.negative_percentage.toFixed(1)}%
                                </small>
                            </div>
                        </div>
                    </div>
                `;
            }
        });

        html += '</div>';
        resultDiv.innerHTML = html;
    }

    // Toggle keywords visibility
    window.toggleKeywords = function(resultId) {
        const section = document.getElementById(resultId);
        const btn = event.currentTarget;

        if (section.classList.contains('show')) {
            section.classList.remove('show');
            btn.innerHTML = '<i class="fas fa-chevron-down"></i> Show Keywords';
        } else {
            section.classList.add('show');
            btn.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Keywords';
        }
    };

    // Load history
    async function loadHistory() {
        if (!historyContainer) return;

        try {
            const response = await fetch('/get_history');
            const data = await response.json();

            if (data.history && data.history.length > 0) {
                historyContainer.innerHTML = '';

                data.history.slice(0, 10).forEach(entry => {
                    const emoji = entry.sentiment.toLowerCase().includes('positive') ? '😊' : '😞';
                    const bgColor = entry.sentiment.toLowerCase().includes('positive') 
                        ? 'rgba(56, 239, 125, 0.15)' 
                        : 'rgba(244, 92, 67, 0.15)';
                    const borderColor = entry.sentiment.toLowerCase().includes('positive') 
                        ? 'rgba(56, 239, 125, 0.3)' 
                        : 'rgba(244, 92, 67, 0.3)';

                    const historyItem = document.createElement('div');
                    historyItem.className = 'alert';
                    historyItem.style.cssText = `
                        background: ${bgColor};
                        backdrop-filter: blur(10px);
                        border: 1px solid ${borderColor};
                        border-radius: 20px;
                        padding: 20px;
                        margin-bottom: 15px;
                        border-left: 4px solid ${borderColor};
                        transition: all 0.3s ease;
                        color: white;
                    `;
                    
                    historyItem.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap; gap: 15px;">
                            <div style="flex: 1; min-width: 200px;">
                                <strong style="font-size: 1.1rem;">${emoji} ${entry.sentiment}</strong>
                                <small style="display: block; margin-top: 8px; opacity: 0.9;">
                                    ${entry.text_preview}
                                </small>
                                <small style="opacity: 0.7; display: block; margin-top: 8px;">
                                    <i class="fas fa-clock"></i> ${new Date(entry.created_at).toLocaleString()}
                                </small>
                            </div>
                            <div style="text-align: right; min-width: 150px;">
                                <small style="display: block; margin-bottom: 5px;">
                                    <strong>✅ ${entry.positive_percentage.toFixed(1)}%</strong>
                                </small>
                                <small style="display: block; margin-bottom: 10px;">
                                    <strong>❌ ${entry.negative_percentage.toFixed(1)}%</strong>
                                </small>
                                <button style="
                                    background: linear-gradient(135deg, #f45c43, #eb3349);
                                    border: none;
                                    border-radius: 10px;
                                    padding: 8px 15px;
                                    color: white;
                                    cursor: pointer;
                                    font-size: 0.85rem;
                                    transition: all 0.3s ease;
                                " onclick="deleteHistory(${entry.id})" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                                    <i class="fas fa-trash"></i> Delete
                                </button>
                            </div>
                        </div>
                    `;
                    
                    historyContainer.appendChild(historyItem);
                });
            } else {
                historyContainer.innerHTML = '<p style="text-align: center; color: rgba(255, 255, 255, 0.5); padding: 20px;">No analysis yet. Start analyzing!</p>';
            }
        } catch (error) {
            console.error('Error loading history:', error);
        }
    }

    // Load statistics
    async function loadStats() {
        try {
            const response = await fetch('/statistics');
            const data = await response.json();

            const totalEl = document.getElementById('total-analyses');
            const positiveEl = document.getElementById('positive-count');
            const negativeEl = document.getElementById('negative-count');
            const accuracyEl = document.getElementById('accuracy-rate');

            if (totalEl) totalEl.textContent = data.total || 0;
            if (positiveEl) positiveEl.textContent = data.positive || 0;
            if (negativeEl) negativeEl.textContent = data.negative || 0;
            if (accuracyEl) {
                const rate = data.total > 0 ? ((data.positive / data.total) * 100).toFixed(1) : 0;
                accuracyEl.textContent = rate + '%';
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    // Delete history entry
    window.deleteHistory = async function(id) {
        if (!confirm('Are you sure you want to delete this analysis?')) return;

        try {
            const response = await fetch(`/delete_analysis/${id}`, { method: 'DELETE' });

            if (response.ok) {
                loadHistory();
                loadStats();
                showAlert('History entry deleted successfully', 'success');
            } else {
                showAlert('Failed to delete history entry', 'danger');
            }
        } catch (error) {
            console.error('Error deleting history:', error);
            showAlert('Error deleting history entry', 'danger');
        }
    };

    // Clear all history
    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to clear all history? This action cannot be undone.')) return;

            try {
                const response = await fetch('/clear_history', { method: 'POST' });
                if (response.ok) {
                    historyContainer.innerHTML = '<p style="text-align: center; color: rgba(255, 255, 255, 0.5); padding: 20px;">No analysis yet. Start analyzing!</p>';
                    document.getElementById('total-analyses').textContent = '0';
                    document.getElementById('positive-count').textContent = '0';
                    document.getElementById('negative-count').textContent = '0';
                    document.getElementById('accuracy-rate').textContent = '0%';
                    showAlert('History cleared successfully', 'success');
                }
            } catch (error) {
                console.error('Error clearing history:', error);
                showAlert('Error clearing history', 'danger');
            }
        });
    }

    // Export CSV
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            window.location.href = '/export/csv';
        });
    }

    // Utility: Scroll to result
    function scrollToResult() {
        setTimeout(() => {
            if (resultDiv) {
                resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }, 300);
    }

    // Utility: Show alert
    function showAlert(message, type) {
        const bgColors = {
            success: 'rgba(56, 239, 125, 0.2)',
            danger: 'rgba(244, 92, 67, 0.2)',
            warning: 'rgba(255, 193, 7, 0.2)'
        };
        const borderColors = {
            success: 'rgba(56, 239, 125, 0.4)',
            danger: 'rgba(244, 92, 67, 0.4)',
            warning: 'rgba(255, 193, 7, 0.4)'
        };

        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert';
        alertDiv.style.cssText = `
            background: ${bgColors[type] || bgColors.warning};
            backdrop-filter: blur(10px);
            border: 1px solid ${borderColors[type] || borderColors.warning};
            border-radius: 20px;
            padding: 20px;
            margin-top: 20px;
            color: white;
            animation: slideUp 0.3s ease;
            position: relative;
        `;
        alertDiv.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    font-size: 1.2rem;
                    cursor: pointer;
                    opacity: 0.7;
                    transition: opacity 0.3s;
                " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.7'">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        if (resultDiv) {
            resultDiv.innerHTML = '';
            resultDiv.appendChild(alertDiv);

            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }
});