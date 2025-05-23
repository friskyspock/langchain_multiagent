// Content-Type: application/javascript
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('interviewSetupForm');
  const topicsContainer = document.getElementById('topicsContainer');
  const addTopicBtn = document.getElementById('addTopicBtn');

  // Add a new topic input field
  addTopicBtn.addEventListener('click', function() {
    const topicInput = document.createElement('div');
    topicInput.className = 'topic-input';
    topicInput.innerHTML = `
      <div class="input-icon-wrapper">
        <i class="fas fa-comment-dots input-icon"></i>
        <input type="text" name="topics[]" placeholder="e.g., Expected salary" required>
      </div>
      <button type="button" class="remove-topic" title="Remove topic"><i class="fas fa-times"></i></button>
    `;
    topicsContainer.appendChild(topicInput);

    // Add event listener to the new remove button
    const removeBtn = topicInput.querySelector('.remove-topic');
    removeBtn.addEventListener('click', function() {
      // Add fade out animation
      topicInput.style.opacity = '0';
      topicInput.style.transform = 'translateY(10px)';
      topicInput.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

      // Remove after animation completes
      setTimeout(() => {
        topicsContainer.removeChild(topicInput);
      }, 300);
    });

    // Focus the new input field
    const newInput = topicInput.querySelector('input');
    newInput.focus();
  });

  // Add event listeners to existing remove buttons
  document.querySelectorAll('.remove-topic').forEach(button => {
    button.addEventListener('click', function() {
      const topicInput = this.parentElement;

      // Add fade out animation
      topicInput.style.opacity = '0';
      topicInput.style.transform = 'translateY(10px)';
      topicInput.style.transition = 'opacity 0.3s ease, transform 0.3s ease';

      // Remove after animation completes
      setTimeout(() => {
        topicsContainer.removeChild(topicInput);
      }, 300);
    });
  });

  // Form validation feedback
  const inputs = form.querySelectorAll('input, textarea');
  inputs.forEach(input => {
    input.addEventListener('blur', function() {
      if (this.checkValidity()) {
        this.classList.add('valid');
        this.classList.remove('invalid');
      } else if (this.value !== '') {
        this.classList.add('invalid');
        this.classList.remove('valid');
      }
    });

    input.addEventListener('input', function() {
      if (this.classList.contains('invalid') && this.checkValidity()) {
        this.classList.remove('invalid');
        this.classList.add('valid');
      }
    });
  });

  // Handle form submission with loading state
  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Show loading state
    const submitBtn = document.getElementById('startInterviewBtn');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Setting up...';
    submitBtn.disabled = true;

    // Collect all topic values
    const topicInputs = document.querySelectorAll('input[name="topics[]"]');
    const topics = Array.from(topicInputs).map(input => input.value);

    // Create interview session data
    const sessionData = {
      candidate_name: document.getElementById('candidateName').value,
      job_title: document.getElementById('jobTitle').value,
      job_description: document.getElementById('jobDescription').value,
      topics_to_cover: topics
    };

    try {
      // Send data to backend to create a session
      const response = await fetch('/p1/recruiter_call_agent/create_interview_session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(sessionData)
      });

      const data = await response.json();

      if (data.status) {
        // Store session ID in localStorage
        localStorage.setItem('interviewSessionId', data.session_id);

        // Show success message before redirect
        submitBtn.innerHTML = '<i class="fas fa-check-circle"></i> Success!';
        submitBtn.style.backgroundColor = 'var(--success-color)';

        // Redirect to the interview page after a short delay
        setTimeout(() => {
          window.location.href = '/p1/recruiter_call_agent/interview';
        }, 800);
      } else {
        // Show error in the UI
        submitBtn.innerHTML = originalBtnText;
        submitBtn.disabled = false;

        // Create error notification
        showNotification('Error: ' + (data.error || 'Failed to create interview session'), 'error');
      }
    } catch (error) {
      console.error('Error:', error);

      // Reset button state
      submitBtn.innerHTML = originalBtnText;
      submitBtn.disabled = false;

      // Show error notification
      showNotification('An error occurred while setting up the interview.', 'error');
    }
  });

  // Helper function to show notifications
  function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Add icon based on type
    let icon = 'info-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'success') icon = 'check-circle';

    notification.innerHTML = `
      <i class="fas fa-${icon}"></i>
      <span>${message}</span>
      <button class="close-notification"><i class="fas fa-times"></i></button>
    `;

    // Add to document
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
      notification.style.opacity = '1';
    }, 10);

    // Add close button functionality
    const closeBtn = notification.querySelector('.close-notification');
    closeBtn.addEventListener('click', () => {
      removeNotification(notification);
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
      removeNotification(notification);
    }, 5000);
  }

  function removeNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    notification.style.opacity = '0';

    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }
});