function ResumeDisplay({ data }) {
  const { contact, summary, skills, experience, education, certifications, languages } = data

  return (
    <div className="space-y-8">
      {/* Contact Card */}
      <section className="bg-slate-800/50 rounded-2xl border border-slate-700/50 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
          <h2 className="text-2xl font-bold text-white">
            {contact?.name || 'Unknown Name'}
          </h2>
          {contact?.location && (
            <p className="text-blue-100 mt-1 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {contact.location}
            </p>
          )}
        </div>
        <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {contact?.email && (
            <ContactItem
              icon={<EmailIcon />}
              label="Email"
              value={contact.email}
              href={`mailto:${contact.email}`}
            />
          )}
          {contact?.phone && (
            <ContactItem
              icon={<PhoneIcon />}
              label="Phone"
              value={contact.phone}
              href={`tel:${contact.phone}`}
            />
          )}
          {contact?.linkedin && (
            <ContactItem
              icon={<LinkedInIcon />}
              label="LinkedIn"
              value="View Profile"
              href={contact.linkedin.startsWith('http') ? contact.linkedin : `https://${contact.linkedin}`}
            />
          )}
        </div>
      </section>

      {/* Summary */}
      {summary && (
        <Section title="Professional Summary" icon={<SummaryIcon />}>
          <p className="text-slate-300 leading-relaxed">{summary}</p>
        </Section>
      )}

      {/* Skills */}
      {skills && skills.length > 0 && (
        <Section title="Skills" icon={<SkillsIcon />}>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 bg-slate-700/50 text-slate-200 rounded-lg text-sm font-medium border border-slate-600/50"
              >
                {skill}
              </span>
            ))}
          </div>
        </Section>
      )}

      {/* Experience */}
      {experience && experience.length > 0 && (
        <Section title="Work Experience" icon={<WorkIcon />}>
          <div className="space-y-6">
            {experience.map((job, idx) => (
              <div key={idx} className="relative pl-6 border-l-2 border-slate-600">
                <div className="absolute -left-[9px] top-0 w-4 h-4 bg-blue-500 rounded-full border-4 border-slate-800" />
                <div className="mb-2">
                  <h4 className="text-lg font-semibold text-white">{job.title || 'Position'}</h4>
                  <p className="text-blue-400">{job.company || 'Company'}</p>
                  {(job.start_date || job.end_date) && (
                    <p className="text-sm text-slate-400 mt-1">
                      {job.start_date} — {job.end_date || 'Present'}
                    </p>
                  )}
                </div>
                {job.description && (
                  <p className="text-slate-300 text-sm mb-2">{job.description}</p>
                )}
                {job.highlights && job.highlights.length > 0 && (
                  <ul className="space-y-1">
                    {job.highlights.map((highlight, hIdx) => (
                      <li key={hIdx} className="text-slate-400 text-sm flex items-start gap-2">
                        <span className="text-blue-400 mt-1">•</span>
                        {highlight}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Education */}
      {education && education.length > 0 && (
        <Section title="Education" icon={<EducationIcon />}>
          <div className="space-y-4">
            {education.map((edu, idx) => (
              <div key={idx} className="p-4 bg-slate-700/30 rounded-xl">
                <h4 className="font-semibold text-white">
                  {edu.degree} {edu.field_of_study && `in ${edu.field_of_study}`}
                </h4>
                <p className="text-blue-400">{edu.institution}</p>
                {(edu.start_date || edu.end_date) && (
                  <p className="text-sm text-slate-400 mt-1">
                    {edu.start_date && `${edu.start_date} — `}{edu.end_date}
                  </p>
                )}
                {edu.gpa && <p className="text-sm text-slate-400">GPA: {edu.gpa}</p>}
              </div>
            ))}
          </div>
        </Section>
      )}

      {/* Certifications */}
      {certifications && certifications.length > 0 && (
        <Section title="Certifications" icon={<CertIcon />}>
          <ul className="space-y-2">
            {certifications.map((cert, idx) => (
              <li key={idx} className="flex items-center gap-3 text-slate-300">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {cert}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Languages */}
      {languages && languages.length > 0 && (
        <Section title="Languages" icon={<LanguageIcon />}>
          <div className="flex flex-wrap gap-2">
            {languages.map((lang, idx) => (
              <span
                key={idx}
                className="px-3 py-1.5 bg-purple-500/20 text-purple-300 rounded-lg text-sm font-medium border border-purple-500/30"
              >
                {lang}
              </span>
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}

function Section({ title, icon, children }) {
  return (
    <section className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6">
      <h3 className="flex items-center gap-3 text-lg font-semibold text-white mb-4">
        <span className="text-slate-400">{icon}</span>
        {title}
      </h3>
      {children}
    </section>
  )
}

function ContactItem({ icon, label, value, href }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center gap-3 p-3 bg-slate-700/30 rounded-xl hover:bg-slate-700/50 transition-colors"
    >
      <div className="text-slate-400">{icon}</div>
      <div>
        <p className="text-xs text-slate-400">{label}</p>
        <p className="text-white text-sm font-medium">{value}</p>
      </div>
    </a>
  )
}

// Icons
function EmailIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  )
}

function PhoneIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
    </svg>
  )
}

function LinkedInIcon() {
  return (
    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  )
}

function SummaryIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
    </svg>
  )
}

function SkillsIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  )
}

function WorkIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  )
}

function EducationIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path d="M12 14l9-5-9-5-9 5 9 5z" />
      <path d="M12 14l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0l6.16-3.422a12.083 12.083 0 01.665 6.479A11.952 11.952 0 0012 20.055a11.952 11.952 0 00-6.824-2.998 12.078 12.078 0 01.665-6.479L12 14zm-4 6v-7.5l4-2.222" />
    </svg>
  )
}

function CertIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
    </svg>
  )
}

function LanguageIcon() {
  return (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
    </svg>
  )
}

export default ResumeDisplay
