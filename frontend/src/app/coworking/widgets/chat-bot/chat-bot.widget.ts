/**
 * @author Kathryn Brown
 * @copyright 2025
 * @license MIT
 */

import { Component, WritableSignal, signal } from '@angular/core';
import { MessageType, Message } from '../../coworking.models';
import { FormControl } from '@angular/forms';

@Component({
  selector: 'chat-bot',
  templateUrl: './chat-bot.widget.html',
  styleUrls: ['./chat-bot.widget.css']
})
export class ChatBot {
  messageCache: WritableSignal<Message[]> = signal([]);
  infoShow: WritableSignal<Boolean> = signal(false);

  chatInput = new FormControl('');

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
    }

    // need to link to backend, for now fake ai response
    const aiMessage = {
      type: MessageType.AIMessage,
      content: 'Helpful insight.'
    };
    this.messageCache.update((messages) => [...messages, aiMessage]);

    this.chatInput.setValue('');
  }

  /** Constructor */
  constructor() {}
}
