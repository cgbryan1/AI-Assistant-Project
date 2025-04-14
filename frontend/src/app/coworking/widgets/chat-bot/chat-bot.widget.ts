/**
 * @author Kathryn Brown
 * @copyright 2025
 * @license MIT
 */

import { Component, WritableSignal, signal } from '@angular/core';
import { MessageType, Message } from '../../coworking.models';
import { FormControl } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'chat-bot',
  templateUrl: './chat-bot.widget.html',
  styleUrls: ['./chat-bot.widget.css']
})
export class ChatBot {
  messageCache: WritableSignal<Message[]> = signal([]);
  infoShow: WritableSignal<Boolean> = signal(false);

  chatInput = new FormControl('');
  endpoint = `/api/ai_request/`;

  /** Constructor */
  constructor(protected http: HttpClient) {}

  infoClicked() {
    this.infoShow.set(!this.infoShow());
    console.log(this.infoShow());
  }

  onChatInput() {
    if (this.chatInput.value) {
      const newMessage = {
        type: MessageType.UserMessage,
        content: this.chatInput.value
      };
      this.messageCache.update((messages) => [...messages, newMessage]);

      // backend
      const params = { user_prompt: `${newMessage.content}` };
      this.http
        .get(`${this.endpoint}`, { params, responseType: 'text' })
        .subscribe((result: string) => {
          console.log(result);
          const aiMessage = {
            type: MessageType.AIMessage,
            content: result.slice(1, result.length - 1) // removing quotes from message
          };
          this.messageCache.update((messages) => [...messages, aiMessage]);
        });

      /* const aiMessage = {     <- dummy meassage
        type: MessageType.AIMessage,
        content: 'Helpful insight.'
      };
      this.messageCache.update((messages) => [...messages, aiMessage]); */

      this.chatInput.setValue(''); // resets to empty input
    }
  }
}
