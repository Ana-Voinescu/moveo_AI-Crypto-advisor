import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import VoteButtons from '../components/shared/VoteButtons'
import * as api from '../services/api'

vi.mock('../services/api')

describe('VoteButtons', () => {
  beforeEach(() => vi.clearAllMocks())

  test('clicking thumbs up calls api.submitVote with true', async () => {
    api.submitVote.mockResolvedValue({})
    render(<VoteButtons contentType="news" contentId="article-1" />)

    fireEvent.click(screen.getByTitle('Helpful'))

    await waitFor(() =>
      expect(api.submitVote).toHaveBeenCalledWith('news', 'article-1', true)
    )
  })

  test('clicking thumbs down calls api.submitVote with false', async () => {
    api.submitVote.mockResolvedValue({})
    render(<VoteButtons contentType="meme" contentId="meme-1" />)

    fireEvent.click(screen.getByTitle('Not helpful'))

    await waitFor(() =>
      expect(api.submitVote).toHaveBeenCalledWith('meme', 'meme-1', false)
    )
  })

  test('thumbs up button gets active class after voting up', async () => {
    api.submitVote.mockResolvedValue({})
    render(<VoteButtons contentType="news" contentId="article-1" />)

    const thumbsUp = screen.getByTitle('Helpful')
    fireEvent.click(thumbsUp)

    await waitFor(() => expect(thumbsUp).toHaveClass('vote-active-up'))
    expect(screen.getByTitle('Not helpful')).not.toHaveClass('vote-active-down')
  })

  test('clicking the same button twice does not call the API a second time', async () => {
    api.submitVote.mockResolvedValue({})
    render(<VoteButtons contentType="news" contentId="article-1" />)

    const thumbsUp = screen.getByTitle('Helpful')
    fireEvent.click(thumbsUp)
    await waitFor(() => expect(api.submitVote).toHaveBeenCalledTimes(1))

    fireEvent.click(thumbsUp)
    expect(api.submitVote).toHaveBeenCalledTimes(1)
  })

  test('initialVote prop restores highlighted state without any click', () => {
    render(<VoteButtons contentType="news" contentId="article-1" initialVote={true} />)
    expect(screen.getByTitle('Helpful')).toHaveClass('vote-active-up')
    expect(screen.getByTitle('Not helpful')).not.toHaveClass('vote-active-down')
  })

  test('API failure is handled silently and button state does not change', async () => {
    api.submitVote.mockRejectedValue(new Error('Network error'))
    render(<VoteButtons contentType="news" contentId="article-1" />)

    fireEvent.click(screen.getByTitle('Helpful'))

    await waitFor(() => expect(api.submitVote).toHaveBeenCalled())
    expect(screen.getByTitle('Helpful')).not.toHaveClass('vote-active-up')
  })
})
