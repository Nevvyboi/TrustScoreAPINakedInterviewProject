document.getElementById('trustForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const clamp05 = (v) => Math.max(0, Math.min(5, Number(v)));
    const data = {
        yearsInNetwork:        clamp05(document.getElementById('yearsInNetwork').value),
        referrals:             clamp05(document.getElementById('referrals').value),
        disciplineIncidents:   clamp05(document.getElementById('disciplineIncidents').value),
        trainingLevel:         clamp05(document.getElementById('trainingLevel').value),
        communityContributions:clamp05(document.getElementById('communityContributions').value)
    };

    const resultEl = document.getElementById('result');

    try {
        const response = await fetch('/calculateOccupantTrustScore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
        });

        if (!response.ok) {
        let detail = '';
        try {
            const err = await response.json();
            detail = err.detail ? JSON.stringify(err.detail) : response.statusText;
        } catch { detail = response.statusText; }
        resultEl.innerHTML = `<span class="error">Request failed (${response.status}). ${detail}</span>`;
        resultEl.classList.add('show');
        return;
        }

        const payload = await response.json();

        const score =
        typeof payload.score === 'number'
            ? payload.score
            : (typeof payload.trustScore === 'number' ? payload.trustScore : NaN);

        const band           = payload.band || '';
        const explanation    = payload.explanation || '';
        const pb             = payload.pointsBreakdown || {};
        const suggestions    = Array.isArray(payload.suggestions) ? payload.suggestions : [];

        const esc = (s) => String(s).replace(/[&<>"'`=\/]/g, c =>
        ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;','/':'&#x2F;','`':'&#x60;','=':'&#x3D;'}[c])
        );

        resultEl.innerHTML = `
        <div class="score">Your trust score: <strong>${isNaN(score) ? '—' : score}</strong>
            ${band ? `<span class="badge">${esc(band)}</span>` : ''}
        </div>
        ${explanation ? `<p>${esc(explanation)}</p>` : ''}
        ${pb ? `
            <details open>
            <summary>How your score was calculated</summary>
            <ul class="breakdown">
                <li>Years in network: ${pb.yearsInNetwork ?? '-' } pts</li>
                <li>Referrals: ${pb.referrals ?? '-' } pts</li>
                <li>Clean record: ${pb.cleanRecord ?? '-' } pts</li>
                <li>Training: ${pb.training ?? '-' } pts</li>
                <li>Contributions: ${pb.communityContributions ?? '-' } pts</li>
            </ul>
            </details>` : ''
        }
        ${suggestions.length ? `
            <details open>
            <summary>Suggestions to improve</summary>
            <ul>${suggestions.map(s => `<li>${esc(s)}</li>`).join('')}</ul>
            </details>` : ''
        }
        `;
        resultEl.classList.add('show');
        const badge = resultEl.querySelector('.badge');
        if (badge) {
            if (payload?.band?.toLowerCase().startsWith('excellent')) badge.classList.add('excellent');
            else if (payload?.band?.toLowerCase().startsWith('good')) badge.classList.add('good');
            else badge.classList.add('review');
        }

    } catch (error) {
        resultEl.innerHTML = `<span class="error">Network error: ${error.message}</span>`;
        resultEl.classList.add('show');
    }
});
